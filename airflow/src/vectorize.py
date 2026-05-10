"""
vectorize.py
------------
Stage 2 of the ML pipeline.

Two modes:

  fit_and_transform(execution_date)
      Called ONCE during init.
      Fits TF-IDF + SVD on the training split text, saves the fitted vectorizer,
      then transforms all three splits (train / val / test).

  transform(execution_date)
      Called EVERY DAY in the daily pipeline.
      Loads the frozen vectorizer and transforms the current day's splits.
      The vectorizer is intentionally never retrained here — retraining it would
      change the feature space and make day-to-day model comparisons unfair.

Both modes save three feature DataFrames to artifacts/features/:
  train_{execution_date}.parquet
  val_{execution_date}.parquet
  test_{execution_date}.parquet

Each DataFrame contains:
  - svd_0 … svd_{N-1}       : latent text features (float)
  - discounted_price, …     : numeric features      (float)
  - main_category            : categorical feature   (string)
  - rating                   : target column         (float)
"""

import logging

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline

from config import (
    CAT_FEATURES,
    FEATURES_DIR,
    NUMERIC_FEATURES,
    PREPROCESSED_DIR,
    SVD_N_COMPONENTS,
    TARGET,
    TFIDF_MAX_FEATURES,
    TRAIN_RATIO,
    VAL_RATIO,
    VECTORIZER_DIR,
    VECTORIZER_PATH,
)

logger = logging.getLogger(__name__)

SVD_COLS = [f"svd_{i}" for i in range(SVD_N_COMPONENTS)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_vectorizer() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=(1, 2),   # unigrams + bigrams
            sublinear_tf=True,    # apply log(1+tf) to dampen high-frequency terms
            min_df=2,             # ignore terms that appear in fewer than 2 docs
        )),
        ("svd", TruncatedSVD(n_components=SVD_N_COMPONENTS, random_state=42)),
    ])


def _sequential_split(df: pd.DataFrame):
    """80 / 10 / 10 sequential split."""
    n = len(df)
    train_end = int(n * TRAIN_RATIO)
    val_end   = int(n * (TRAIN_RATIO + VAL_RATIO))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]


def _assemble_features(svd_matrix: np.ndarray, df: pd.DataFrame) -> pd.DataFrame:
    """Concatenate SVD columns with numeric and categorical columns + target."""
    svd_df = pd.DataFrame(svd_matrix, columns=SVD_COLS, index=df.index)
    structured = df[NUMERIC_FEATURES + CAT_FEATURES + [TARGET]].reset_index(drop=True)
    return pd.concat([svd_df.reset_index(drop=True), structured], axis=1)


def _save_splits(train_df, val_df, test_df, execution_date: str) -> None:
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in [("train", train_df), ("val", val_df), ("test", test_df)]:
        path = FEATURES_DIR / f"{name}_{execution_date}.parquet"
        data.to_parquet(path, index=False)
        logger.info("Saved %s features → %s  (%d rows)", name, path, len(data))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fit_and_transform(execution_date: str) -> dict:
    df = pd.read_parquet(PREPROCESSED_DIR / f"data_{execution_date}.parquet")
    train_df, val_df, test_df = _sequential_split(df)
    logger.info("Split sizes — train: %d | val: %d | test: %d",
                len(train_df), len(val_df), len(test_df))

    logger.info("Fitting TF-IDF + SVD on training text…")
    vec = _build_vectorizer()
    train_svd = vec.fit_transform(train_df["text_clean"])

    VECTORIZER_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vec, VECTORIZER_PATH)
    logger.info("Vectorizer saved → %s", VECTORIZER_PATH)

    val_svd  = vec.transform(val_df["text_clean"])
    test_svd = vec.transform(test_df["text_clean"])

    _save_splits(
        _assemble_features(train_svd, train_df),
        _assemble_features(val_svd,   val_df),
        _assemble_features(test_svd,  test_df),
        execution_date,
    )
    return {"execution_date": execution_date}


def transform(execution_date: str) -> dict:
    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Vectorizer not found at {VECTORIZER_PATH}. Run init_pipeline first."
        )
    vec = joblib.load(VECTORIZER_PATH)
    logger.info("Vectorizer loaded from %s", VECTORIZER_PATH)

    df = pd.read_parquet(PREPROCESSED_DIR / f"data_{execution_date}.parquet")
    train_df, val_df, test_df = _sequential_split(df)
    logger.info("Split sizes — train: %d | val: %d | test: %d",
                len(train_df), len(val_df), len(test_df))

    _save_splits(
        _assemble_features(vec.transform(train_df["text_clean"]), train_df),
        _assemble_features(vec.transform(val_df["text_clean"]),   val_df),
        _assemble_features(vec.transform(test_df["text_clean"]),  test_df),
        execution_date,
    )
    return {"execution_date": execution_date}
