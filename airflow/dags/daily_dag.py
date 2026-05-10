"""
daily_dag.py
------------
Daily retraining pipeline. Runs automatically every day at midnight UTC.

WHAT HAPPENS EACH DAY
---------------------
Airflow passes a "logical date" (called ds, short for data stamp) to each
task. For a daily DAG, ds is the date the run represents — e.g. "2024-01-02"
for the first daily run.

We use ds to simulate new data arriving:
  available fraction = 0.80 + days_since_start × 0.02

So on 2024-01-02 we use 82 % of the dataset, on 2024-01-03 → 84 %, etc.
After 10 days all data is available.

TASK FLOW
---------
preprocess  → cleans the current day's data slice
vectorize   → applies the FROZEN vectorizer (never retrained — see vectorize.py)
train       → trains a fresh CatBoost model from scratch on the larger dataset
evaluate    → RMSE/MAE/MAPE/R², compares vs baseline and vs yesterday's model

AIRFLOW CONCEPTS USED
---------------------
schedule="@daily"   — Airflow triggers this automatically at midnight UTC every day
start_date          — the first date for which a run should exist
catchup=False       — if Airflow was offline for several days, do NOT run all
                      missed dates; just run from "now" going forward.
                      Set to True if you want to simulate all past days quickly.
**context           — Airflow injects a context dict into every @task function
                      when you declare **context in the signature.
context["ds"]       — the execution date as a "YYYY-MM-DD" string
"""

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="daily_pipeline",
    description="Daily retraining: preprocess → vectorize → train → evaluate",
    schedule="@daily",
    start_date=datetime(2024, 1, 2),   # day after init
    catchup=False,
    tags=["ml", "daily"],
)
def daily_pipeline():

    @task()
    def preprocess(**context):
        """
        context["ds"] is injected by Airflow — it's the execution date (YYYY-MM-DD).
        We pass it to run() so it knows how much data is "available" today.
        """
        from preprocess import run
        return run(context["ds"])

    @task()
    def vectorize(preprocessed_path: str, **context):
        """
        Loads the vectorizer saved by init_pipeline and applies it to today's data.
        We deliberately never refit it — see the docstring in vectorize.py.
        """
        from vectorize import transform
        return transform(context["ds"])

    @task()
    def train(vectorize_result: dict, **context):
        """
        Trains a fresh model on all training data available today.
        Saved as model_{ds}.cbm so previous versions are not overwritten.
        """
        from train import run
        return run(context["ds"])

    @task()
    def evaluate(model_path: str, **context):
        """
        Scores today's model AND the previous model on the same test set,
        so the comparison is always apples-to-apples.
        """
        from evaluate import run
        return run(context["ds"])

    preprocessed = preprocess()
    vectorized    = vectorize(preprocessed)
    trained       = train(vectorized)
    evaluate(trained)


daily_pipeline()
