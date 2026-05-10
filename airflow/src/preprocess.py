"""
preprocess.py
-------------
Stage 1 of the ML pipeline.

Loads the raw CSV, slices it to the rows "available" on a given execution date,
cleans numeric / categorical / text columns, and saves a parquet file to
  artifacts/preprocessed/data_{execution_date}.parquet

Public API
----------
run(execution_date: str) -> str
    execution_date: ISO-format date string, e.g. "2024-01-01"
    returns: absolute path of the saved parquet file
"""

import re
import logging
from typing import Optional

import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from config import (
    DATA_DIR,
    MODELS_DIR,
    PREPROCESSED_DIR,
    TEXT_COLS,
    NUMERIC_FEATURES,
    TARGET,
    INITIAL_FRACTION,
    DAILY_INCREMENT,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NLTK setup  (corpora are baked into the Docker image via the Dockerfile)
# ---------------------------------------------------------------------------
try:
    _STOP_WORDS = set(stopwords.words("english"))
    _lemmatizer = WordNetLemmatizer()
    _lemmatizer.lemmatize("warmup")   # triggers lazy resource load
except LookupError:
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)
    _STOP_WORDS = set(stopwords.words("english"))
    _lemmatizer = WordNetLemmatizer()


# ---------------------------------------------------------------------------
# Column-level cleaners
# ---------------------------------------------------------------------------

def _to_float(value, strip_chars: str = "") -> Optional[float]:
    """Strip currency/percent symbols and convert to float."""
    if pd.isna(value):
        return np.nan
    s = re.sub(rf"[{re.escape(strip_chars)}\s,]", "", str(value))
    try:
        return float(s)
    except ValueError:
        return np.nan


def _clean_rating(value) -> Optional[float]:
    """Handle edge cases like '3|2' (take the first token) or non-numeric."""
    if pd.isna(value):
        return np.nan
    return _to_float(str(value).split("|")[0])


def _extract_main_category(category) -> str:
    """'Electronics|Cables|HDMI'  →  'Electronics'"""
    if pd.isna(category):
        return "Unknown"
    return str(category).split("|")[0].strip() or "Unknown"


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def clean_text(text) -> str:
    """
    Full cleaning pipeline applied to the concatenated text blob:
      1. Lowercase
      2. Remove URLs
      3. Remove everything except letters and spaces
      4. Remove stopwords
      5. Lemmatize
    """
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)  # strip URLs
    text = re.sub(r"[^a-z\s]", " ", text)               # letters only
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [
        _lemmatizer.lemmatize(tok)
        for tok in text.split()
        if tok not in _STOP_WORDS and len(tok) > 2
    ]
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Data-availability simulation
# ---------------------------------------------------------------------------

def _available_fraction() -> float:
    """
    Determines how much of the dataset is "available" by counting how many
    trained models already exist in artifacts/models/.

    This approach is calendar-independent — the simulation works correctly
    regardless of when you actually run the pipeline:
      init run  : 0 models saved yet  → 0.80 (80 % of rows)
      1st daily : 1 model (init)      → 0.82
      2nd daily : 2 models            → 0.84
      …and so on, capped at 1.0
    """
    days_elapsed = len(list(MODELS_DIR.glob("model_*.cbm")))
    return min(INITIAL_FRACTION + days_elapsed * DAILY_INCREMENT, 1.0)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(execution_date: str) -> str:
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV file found in {DATA_DIR}")

    logger.info("Loading %s", csv_files[0])
    df = pd.read_csv(csv_files[0])

    # Slice to "available" rows
    fraction = _available_fraction()
    n_rows = int(len(df) * fraction)
    df = df.iloc[:n_rows].copy()
    logger.info("Date %s → %.0f%% of data → %d rows", execution_date, fraction * 100, n_rows)

    # Numeric features
    df["discounted_price"]    = df["discounted_price"].apply(lambda x: _to_float(x, "₹"))
    df["actual_price"]        = df["actual_price"].apply(lambda x: _to_float(x, "₹"))
    df["discount_percentage"] = df["discount_percentage"].apply(lambda x: _to_float(x, "%"))
    df["rating_count"]        = df["rating_count"].apply(_to_float)

    # Target
    df[TARGET] = df[TARGET].apply(_clean_rating)

    # Categorical
    df["main_category"] = df["category"].apply(_extract_main_category)

    # Text: concatenate three columns then clean
    df["text_clean"] = (
        df[TEXT_COLS].fillna("").astype(str).agg(" ".join, axis=1).apply(clean_text)
    )

    # Drop rows with missing target or numeric features
    before = len(df)
    df = df.dropna(subset=[TARGET] + NUMERIC_FEATURES).reset_index(drop=True)
    logger.info("Dropped %d rows with missing values → %d remain", before - len(df), len(df))

    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PREPROCESSED_DIR / f"data_{execution_date}.parquet"
    df.to_parquet(out_path, index=False)
    logger.info("Saved → %s", out_path)
    return str(out_path)
