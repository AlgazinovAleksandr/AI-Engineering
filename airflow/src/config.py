import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------
# Inside Docker the default is /opt/airflow.
# When running locally (e.g. main.py), set AIRFLOW_HOME to the project root
# before importing this module and all paths will resolve correctly.
BASE_DIR = Path(os.environ.get("AIRFLOW_HOME", "/opt/airflow"))
DATA_DIR = BASE_DIR / "data"

ARTIFACTS_DIR  = BASE_DIR / "artifacts"
VECTORIZER_DIR = ARTIFACTS_DIR / "vectorizer"
MODELS_DIR     = ARTIFACTS_DIR / "models"
METRICS_DIR    = ARTIFACTS_DIR / "metrics"
PREPROCESSED_DIR = ARTIFACTS_DIR / "preprocessed"
FEATURES_DIR   = ARTIFACTS_DIR / "features"

VECTORIZER_PATH      = VECTORIZER_DIR / "tfidf_svd.joblib"
METRICS_HISTORY_PATH = METRICS_DIR / "history.json"

# ---------------------------------------------------------------------------
# Data-simulation parameters
# ---------------------------------------------------------------------------
# On "day 0" (init run) the first INITIAL_FRACTION of rows are available.
# Each subsequent day adds DAILY_INCREMENT more rows (simulates new data arriving).
INITIAL_FRACTION = 0.80
DAILY_INCREMENT  = 0.02

# Sequential split ratios applied to whatever data is available on a given day.
TRAIN_RATIO = 0.80
VAL_RATIO   = 0.10
# TEST_RATIO is implicitly 1 - TRAIN_RATIO - VAL_RATIO = 0.10

# ---------------------------------------------------------------------------
# Feature definitions
# ---------------------------------------------------------------------------
TEXT_COLS        = ["review_title", "review_content", "about_product"]
NUMERIC_FEATURES = ["discounted_price", "actual_price", "discount_percentage", "rating_count"]
CAT_FEATURES     = ["main_category"]
TARGET           = "rating"

# ---------------------------------------------------------------------------
# TF-IDF + SVD
# ---------------------------------------------------------------------------
TFIDF_MAX_FEATURES = 10_000   # vocabulary cap (dataset is small: 1465 rows)
SVD_N_COMPONENTS   = 50       # latent text dimensions fed to CatBoost

# ---------------------------------------------------------------------------
# CatBoost
# ---------------------------------------------------------------------------
CB_ITERATIONS           = 400
CB_LEARNING_RATE        = 0.05
CB_DEPTH                = 5
CB_RANDOM_SEED          = 42
CB_EARLY_STOPPING_ROUNDS = 40
CB_EVAL_METRIC          = "RMSE"
