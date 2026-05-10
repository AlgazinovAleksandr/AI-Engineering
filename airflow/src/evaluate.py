"""
evaluate.py
-----------
Stage 4 of the ML pipeline.

Evaluates the current model on the test set and computes four metrics:
  RMSE, MAE, MAPE, R²

Also runs two comparisons:
  1. vs. baseline  — predict the training-set mean rating for every sample
  2. vs. previous model — load the most recently saved model and score it on
                          the same test set

Results are appended to artifacts/metrics/history.json so you can track
how performance evolves as more data arrives each day.

Public API
----------
run(execution_date: str) -> dict
    returns: the metrics record for this run
"""

import json
import logging
from datetime import date as Date
from typing import Optional

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor, Pool

from config import (
    CAT_FEATURES,
    FEATURES_DIR,
    METRICS_DIR,
    METRICS_HISTORY_PATH,
    MODELS_DIR,
    TARGET,
)
from train import get_model_path

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Metric functions
# ---------------------------------------------------------------------------

def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # Amazon ratings are 1-5, so y_true is never 0 → no division-by-zero risk.
    return float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)


def r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "rmse": round(rmse(y_true, y_pred), 6),
        "mae":  round(mae(y_true,  y_pred), 6),
        "mape": round(mape(y_true, y_pred), 6),
        "r2":   round(r2(y_true,   y_pred), 6),
    }


# ---------------------------------------------------------------------------
# Previous-model lookup
# ---------------------------------------------------------------------------

def _find_previous_model(execution_date: str) -> Optional[Path]:
    """Return the path of the most recently saved model older than execution_date."""
    current = Date.fromisoformat(execution_date)
    candidates = []
    for p in MODELS_DIR.glob("model_*.cbm"):
        try:
            d = Date.fromisoformat(p.stem.replace("model_", ""))
            if d < current:
                candidates.append((d, p))
        except ValueError:
            pass
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(execution_date: str) -> dict:
    test_df  = pd.read_parquet(FEATURES_DIR / f"test_{execution_date}.parquet")
    train_df = pd.read_parquet(FEATURES_DIR / f"train_{execution_date}.parquet")

    feature_cols = [c for c in test_df.columns if c != TARGET]
    cat_indices  = [feature_cols.index(c) for c in CAT_FEATURES if c in feature_cols]

    y_test  = test_df[TARGET].values
    y_train = train_df[TARGET].values
    test_pool = Pool(test_df[feature_cols], cat_features=cat_indices)

    # --- Current model ---
    model = CatBoostRegressor()
    model.load_model(str(get_model_path(execution_date)))
    current_metrics = compute_metrics(y_test, model.predict(test_pool))
    logger.info("Current model  → %s", current_metrics)

    # --- Baseline: always predict the training-set mean ---
    baseline_pred    = np.full_like(y_test, fill_value=y_train.mean(), dtype=float)
    baseline_metrics = compute_metrics(y_test, baseline_pred)
    logger.info("Baseline       → %s", baseline_metrics)

    # --- Previous model (if any) ---
    prev_metrics = None
    prev_path = _find_previous_model(execution_date)
    if prev_path:
        prev_model = CatBoostRegressor()
        prev_model.load_model(str(prev_path))
        prev_metrics = compute_metrics(y_test, prev_model.predict(test_pool))
        logger.info("Previous model (%s) → %s", prev_path.name, prev_metrics)
    else:
        logger.info("No previous model found — skipping comparison.")

    # --- Build record ---
    record: dict = {
        "execution_date": execution_date,
        "test_size":      int(len(y_test)),
        "current_model":  current_metrics,
        "baseline":       baseline_metrics,
        "previous_model": prev_metrics,
    }

    if prev_metrics:
        # Positive value means current model is better (lower error / higher R²)
        record["improvement_vs_previous"] = {
            "rmse": round(prev_metrics["rmse"] - current_metrics["rmse"], 6),
            "mae":  round(prev_metrics["mae"]  - current_metrics["mae"],  6),
            "mape": round(prev_metrics["mape"] - current_metrics["mape"], 6),
            "r2":   round(current_metrics["r2"] - prev_metrics["r2"],     6),
        }
        logger.info("Δ vs previous  → %s", record["improvement_vs_previous"])

    # --- Persist ---
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    history = []
    if METRICS_HISTORY_PATH.exists():
        with open(METRICS_HISTORY_PATH) as f:
            history = json.load(f)

    history = [h for h in history if h["execution_date"] != execution_date]
    history.append(record)
    history.sort(key=lambda x: x["execution_date"])

    with open(METRICS_HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)
    logger.info("Metrics saved → %s", METRICS_HISTORY_PATH)

    return record
