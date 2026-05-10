"""
main.py
-------
Standalone end-to-end test for the ML pipeline. Runs outside Docker/Airflow.

Executes two full pipeline cycles:
  Cycle 1 — init  : uses the first 80% of data, fits the vectorizer
  Cycle 2 — daily : uses 82% of data, loads frozen vectorizer, compares models

Usage (from the airflow/ directory):
    pip install -r requirements.txt
    python src/main.py

Artifacts are written to airflow/artifacts/ and cleaned on each run.
"""

import logging
import os
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Redirect all paths to the local project root BEFORE importing anything else.
# config.py reads AIRFLOW_HOME on import; this must come first.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.environ["AIRFLOW_HOME"] = str(PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).parent))  # make src/ importable

import config  # noqa: E402 (intentionally after env setup)
from preprocess import run as preprocess
from vectorize import fit_and_transform, transform
from train import run as train
from evaluate import run as evaluate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(name)-20s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")

DATE_INIT  = "2024-01-01"
DATE_DAY1  = "2024-01-02"


def clean_artifacts() -> None:
    """Delete all runtime artifacts so every local run starts from scratch."""
    if config.ARTIFACTS_DIR.exists():
        shutil.rmtree(config.ARTIFACTS_DIR)
        logger.info("Cleaned %s", config.ARTIFACTS_DIR)


def run_cycle_1() -> None:
    """Init cycle: fit vectorizer + train first model on 80% of data."""
    logger.info("=" * 60)
    logger.info("CYCLE 1 — init (%.0f%% of data)", config.INITIAL_FRACTION * 100)
    logger.info("=" * 60)

    preprocess(DATE_INIT)
    fit_and_transform(DATE_INIT)
    train(DATE_INIT)
    result = evaluate(DATE_INIT)

    logger.info("Current model : %s", result["current_model"])
    logger.info("Baseline      : %s", result["baseline"])


def run_cycle_2() -> None:
    """Daily cycle: load frozen vectorizer + train on 82% + compare models."""
    frac = config.INITIAL_FRACTION + config.DAILY_INCREMENT
    logger.info("=" * 60)
    logger.info("CYCLE 2 — daily (%.0f%% of data)", frac * 100)
    logger.info("=" * 60)

    preprocess(DATE_DAY1)
    transform(DATE_DAY1)
    train(DATE_DAY1)
    result = evaluate(DATE_DAY1)

    logger.info("Current model : %s", result["current_model"])
    logger.info("Previous model: %s", result["previous_model"])
    logger.info("Improvement   : %s", result.get("improvement_vs_previous"))


if __name__ == "__main__":
    clean_artifacts()
    run_cycle_1()
    run_cycle_2()
    logger.info("Done. Full results → %s", config.METRICS_HISTORY_PATH)
