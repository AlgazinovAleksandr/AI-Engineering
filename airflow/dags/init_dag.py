"""
init_dag.py
-----------
One-time pipeline: fits the vectorizer and trains the first model.

HOW TO RUN
----------
This DAG has schedule=None, which means Airflow will NEVER trigger it
automatically. You must trigger it manually:
  1. Open the Airflow UI at http://localhost:8080
  2. Find "init_pipeline" in the DAG list
  3. Click the ▶ (Play) button on the right → "Trigger DAG"

Run this ONCE before starting the daily pipeline.

WHAT EACH TASK DOES
-------------------
preprocess  → Loads the first 80 % of rows from amazon.csv, cleans text and
              numeric columns, saves data_2024-01-01.parquet

vectorize   → Fits TF-IDF + SVD on training text, saves the vectorizer to
              artifacts/vectorizer/, transforms train/val/test and saves three
              feature DataFrames to artifacts/features/

train       → Trains a CatBoost regression model on the feature DataFrame,
              saves model_2024-01-01.cbm to artifacts/models/

evaluate    → Computes RMSE / MAE / MAPE / R² on the test set,
              compares vs. the naive baseline (predict average rating),
              saves results to artifacts/metrics/history.json

AIRFLOW CONCEPTS USED
---------------------
@dag        — decorator that turns a Python function into a DAG definition
@task       — decorator that turns a Python function into a Task node
schedule=None — never auto-triggered; manual trigger only
catchup=False — if somehow missed, don't backfill
>>          — defines execution order between tasks
"""

from datetime import datetime

from airflow.decorators import dag, task
# if you are using a newer version of Airflow, the above import may be:
# from airflow.sdk import dag, task - same as before, just a different import path

INIT_DATE = "2024-01-01"


@dag(
    dag_id="init_pipeline",
    description="One-time init: fit vectorizer + train first model on 80% of data",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml", "init"],
)
def init_pipeline():

    @task()
    def preprocess():
        from preprocess import run
        return run(INIT_DATE)

    @task()
    def vectorize(preprocessed_path: str):
        from vectorize import fit_and_transform
        return fit_and_transform(INIT_DATE)

    @task()
    def train(vectorize_result: dict):
        from train import run
        return run(INIT_DATE)

    @task()
    def evaluate(model_path: str):
        from evaluate import run
        return run(INIT_DATE)

    # Execution order: each task receives the output of the previous one.
    # Airflow uses these return values to draw the dependency arrows in the UI.
    preprocessed = preprocess()
    vectorized    = vectorize(preprocessed)
    trained       = train(vectorized)
    evaluate(trained)


init_pipeline()
