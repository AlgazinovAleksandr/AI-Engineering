# Airflow Key Concepts

## What is Airflow

Airflow is a platform for scheduling and monitoring workflows. You define a workflow as a Python file, tell Airflow when to run it, and Airflow takes care of the rest: triggering runs on schedule, retrying on failure, logging every task, and showing you the status in a web UI.

The core idea: instead of running scripts manually or chaining cron jobs, you describe your pipeline as code and Airflow manages its execution.

---

## DAG

DAG stands for **Directed Acyclic Graph**. It is the Airflow word for "pipeline" or "workflow".

- **Directed** — tasks run in a defined order (A → B → C)
- **Acyclic** — no loops; you can't go back to a previous task
- **Graph** — multiple tasks connected by dependencies

You define a DAG in a Python file inside the `dags/` folder. Airflow scans that folder automatically and registers any DAG it finds.

In this project we use the **TaskFlow API** — the modern way to define DAGs using decorators:

```python
from airflow.decorators import dag, task

@dag(schedule="@daily", start_date=datetime(2024, 1, 2), catchup=False)
def my_pipeline():

    @task()
    def step_one():
        return "result"

    @task()
    def step_two(input):
        print(input)

    step_two(step_one())   # defines the order: step_one → step_two

my_pipeline()              # this line registers the DAG with Airflow
```

---

## Task

A Task is a single unit of work inside a DAG — one Python function decorated with `@task`. Airflow runs each task independently, logs its output separately, and tracks its success or failure individually.

If one task fails, Airflow can retry just that task without rerunning the whole pipeline.

**How tasks pass data to each other:**

With the TaskFlow API, a task's return value is automatically passed as an argument to the next task:

```python
preprocessed = preprocess()   # returns a file path string
vectorized = vectorize(preprocessed)  # receives that string
```

For small values (strings, numbers, dicts) Airflow stores the return value in its database and passes it along. For large data (DataFrames, model files) we instead save to disk and pass the file path — which is what this pipeline does.

---

## schedule

Defines how often a DAG runs automatically.

| Value | Meaning |
|---|---|
| `"@daily"` | Once a day at midnight UTC |
| `"@hourly"` | Once an hour |
| `"@weekly"` | Once a week |
| `"0 6 * * *"` | Cron expression — 6:00 AM every day |
| `None` | Never runs automatically; manual trigger only |

In this project:
- `init_pipeline` uses `schedule=None` — you trigger it once manually
- `daily_pipeline` uses `schedule="@daily"` — Airflow triggers it every night automatically

---

## start_date

The date from which the DAG is considered "active". Airflow will not create runs for dates before `start_date`.

For scheduled DAGs, the first run covers the interval that starts at `start_date`. For example, with `start_date=datetime(2024, 1, 2)` and `schedule="@daily"`, the first run represents January 2nd.

For `schedule=None` DAGs (like `init_pipeline`), `start_date` is ignored in practice — the DAG is always triggered manually so the date is irrelevant.

---

## catchup

When Airflow starts (or when you add a new DAG with a `start_date` in the past), it can optionally **backfill** all the missed runs between `start_date` and today.

- `catchup=True` — Airflow creates one run for every missed interval. With `start_date` two years ago and `schedule="@daily"`, that's ~730 runs triggered immediately.
- `catchup=False` — ignore all missed runs, start fresh from now.

This project uses `catchup=False` because we're simulating days manually, not replaying history.

---

## execution_date and ds

Every DAG run has a **logical date** — the date the run *represents*, not necessarily the date it physically ran.

For a daily DAG, a run that executes on May 11 at midnight *represents* May 10 (the start of the completed interval). Airflow calls this the `execution_date` or `ds` (data stamp).

Inside a `@task` function you access it via the context dictionary:

```python
@task()
def preprocess(**context):
    ds = context["ds"]   # e.g. "2024-01-02"
    print(f"Processing data for {ds}")
```

Airflow automatically injects `**context` when you declare it in the function signature. You don't pass it yourself.

In this project `ds` is used as a version tag for output files:
- `data_2024-01-02.parquet`
- `model_2024-01-02.cbm`

This way each day's artifacts are kept separately and never overwritten.

---

## The four Docker services

When you run `docker compose up`, four services start:

```
postgres  →  airflow-init  →  airflow-webserver
                           →  airflow-scheduler
```

| Service | Role |
|---|---|
| **postgres** | Stores all Airflow metadata: DAG definitions, task states, logs, run history |
| **airflow-init** | Runs once on startup: creates the DB schema and the admin user, then exits |
| **airflow-webserver** | Serves the UI at http://localhost:8080 |
| **airflow-scheduler** | Reads DAG files, decides when to trigger runs, and (with LocalExecutor) also executes the tasks |

**LocalExecutor** means the scheduler runs tasks as subprocesses of itself — no separate worker containers needed. Simple and sufficient for a single machine.

---

## How a DAG file becomes a pipeline

1. You place a `.py` file in `dags/`
2. The scheduler scans that folder every few seconds
3. It imports the file, finds the `@dag`-decorated function, and calls it — this *registers* the DAG
4. The last line of every DAG file (`my_pipeline()`) is what triggers registration

This is why DAG files must not have slow code at the top level — the scheduler imports them repeatedly.

---

## The UI walkthrough

After `docker compose up`, open **http://localhost:8080**.

- **DAGs list** — shows all registered DAGs, their schedule, last run status, and a toggle to pause/unpause
- **▶ button** — manually triggers a DAG run
- **Graph view** — shows the task dependency graph; click a task to see its logs
- **Grid view** — shows a matrix of all runs × all tasks; green = success, red = failed, yellow = running
- Click any task → **Logs** tab to see its stdout (where all `logger.info(...)` output goes)

---

## Summary

```
DAG        = the whole pipeline (Python file in dags/)
Task       = one step in the pipeline (@task function)
schedule   = when to run automatically ("@daily", None, cron, …)
start_date = the earliest date the DAG is active
catchup    = whether to backfill missed runs (False = don't)
ds         = the logical date of a specific run, injected via context["ds"]
scheduler  = the Airflow process that triggers and runs tasks
```
