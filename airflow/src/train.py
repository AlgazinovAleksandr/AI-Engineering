"""
train.py
--------
Stage 3 of the ML pipeline.

Loads the feature DataFrames produced by vectorize.py, trains a CatBoost
regression model, and saves it to:
  artifacts/models/model_{execution_date}.cbm

CatBoost is told which column is categorical (main_category) so it applies
its internal target-encoding rather than requiring us to one-hot encode.

Public API
----------
run(execution_date: str) -> str
    returns: absolute path of the saved model file
"""

import logging
from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor, Pool

from config import (
    CAT_FEATURES,
    CB_DEPTH,
    CB_EARLY_STOPPING_ROUNDS,
    CB_EVAL_METRIC,
    CB_ITERATIONS,
    CB_LEARNING_RATE,
    CB_RANDOM_SEED,
    FEATURES_DIR,
    MODELS_DIR,
    TARGET,
)

logger = logging.getLogger(__name__)


def get_model_path(execution_date: str) -> Path:
    return MODELS_DIR / f"model_{execution_date}.cbm"


def run(execution_date: str) -> str:
    train_df = pd.read_parquet(FEATURES_DIR / f"train_{execution_date}.parquet")
    val_df   = pd.read_parquet(FEATURES_DIR / f"val_{execution_date}.parquet")

    feature_cols = [c for c in train_df.columns if c != TARGET]

    # CatBoost accepts categorical features by column index.
    # main_category is the only string column; all SVD/numeric columns are float.
    cat_indices = [feature_cols.index(c) for c in CAT_FEATURES if c in feature_cols]

    train_pool = Pool(train_df[feature_cols], label=train_df[TARGET], cat_features=cat_indices)
    val_pool   = Pool(val_df[feature_cols],   label=val_df[TARGET],   cat_features=cat_indices)

    model = CatBoostRegressor(
        iterations=CB_ITERATIONS,
        learning_rate=CB_LEARNING_RATE,
        depth=CB_DEPTH,
        random_seed=CB_RANDOM_SEED,
        eval_metric=CB_EVAL_METRIC,
        early_stopping_rounds=CB_EARLY_STOPPING_ROUNDS,
        verbose=100,
    )

    logger.info("Training CatBoost — train rows: %d, val rows: %d",
                len(train_df), len(val_df))
    model.fit(train_pool, eval_set=val_pool)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = get_model_path(execution_date)
    model.save_model(str(model_path))
    logger.info("Model saved → %s  (best iteration: %d)",
                model_path, model.get_best_iteration())

    return str(model_path)
