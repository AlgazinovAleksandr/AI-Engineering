# How to get the Airflow docker-compose.yaml

The Airflow team provides an official ready-made file. Download it instead of writing from scratch:

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/3.2.1/docker-compose.yaml'
```

---

## What to simplify

The official file is written for production and uses **CeleryExecutor** — multiple worker containers, a Redis message broker, and a Flower monitoring UI. For a single machine this is overkill. Here is what to strip out:

**Remove these services entirely:**
- `redis` — the message broker Celery uses to distribute tasks to workers
- `airflow-worker` — the Celery worker containers that execute tasks
- `flower` — a web UI for monitoring Celery workers

**Change the executor:**
```yaml
# from
AIRFLOW__CORE__EXECUTOR: CeleryExecutor

# to
AIRFLOW__CORE__EXECUTOR: LocalExecutor
```

With LocalExecutor the scheduler runs tasks itself as subprocesses — no workers or Redis needed.

**Remove the Celery connection string** (only needed for CeleryExecutor):
```yaml
# remove this line
AIRFLOW__CELERY__RESULT_BACKEND: ...
AIRFLOW__CELERY__BROKER_URL: ...
```

After these removals you are left with four services: `postgres`, `airflow-init`, `airflow-webserver`, `airflow-scheduler` — which is exactly what we have in this project.

---

## What to add for your project

**Mount your project folders** so containers can see your code and data:

```yaml
volumes:
  - ./dags:/opt/airflow/dags
  - ./src:/opt/airflow/src
  - ./data:/opt/airflow/data
  - ./artifacts:/opt/airflow/artifacts
```

**Add PYTHONPATH** if your DAGs import from a `src/` folder:

```yaml
environment:
  PYTHONPATH: /opt/airflow/src
```

**Point to your Dockerfile** if you need custom packages (the official file uses a pre-built image):

```yaml
# from
image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.9.3}

# to
build: .
```

**Move credentials to `.env`** instead of hardcoding them in the file (see `.env.example` in this project).
