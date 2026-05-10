### Why use Airflow

**Let's take a look at the real examples**

##### Case 1: Consider the ETL pipeline case:

E - extract the stock market data using API
T - convert currencies to USD, fill the missing data, drop the unnecessary columns, etc
L - load the data to the database

Suppose you need to do this every night. You can do something like this:

```python
import requests
import pandas as pd
import sqlite3

# extract
response = requests.get('https://api.example.com/stock')
data = response.json()

# transform
df = pd.DataFrame(data)
df['price_usd'] = df['price_eur'] / 1.1
df = df.drop(columns=['price_eur'])

# load
conn = sqlite3.connect('stock.db')
df.to_sql('stock', conn, if_exists='replace')
```

And every night you will run this script manually. That's actually what I had to do several years ago for my bachelor thesis...

Alternatively, you can use cron jobs to run this script every night. Possible issues:

+ what if something breaks? You will need to setup retries logic by yourself. And once the pipeline gets big, there will be too many exceptions and the code will become messy and hard to debug

+ also, you will need to setup the logging and monitoring by yourself

+ something else...

##### Case 2: Suppose you are a Machine Learning Engineer at the marketplace. Marketplaces have a lot of machine learning pipelines that need to be either trained or executed every day, or even once in few hours / minutes. Examples:

+ Recommendation System (new items come out, as well as new customer data, and the pipeline should be refined based on that). The ML pipeline may involve:

1. Collect yesterday’s user behavior

2. Aggregate clicks/purchases

3. Build user embeddings

4. Build product embeddings

5. Train recommendation model

6. Evaluate CTR metrics

7. Deploy model

8. Refresh recommendation cache

+ Fraud Detection (since new transatctions come in every second, the pipeline should be executed very often). The pipeline may involve:

1. Pull transaction data

2. Compute suspicious activity features

3. Score sellers with fraud model

4. Flag risky accounts

5. Send alerts to moderation team

+ Other examples might include dynamic pricing, search ranking, etc.

In all these cases, you will need to run a lot of different scripts in a certain order. Hence, there is a clear motivation to automate it as much as possible. Airflow does that!

In this repository, we will take a look at the simple ML-pipeline that includes multiple stages, and we will setup the Airflow to run it automatically every day

---

### Project: Amazon Product Rating Prediction Pipeline

**Goal:** predict a product's star rating (1–5) from its reviews, description, and pricing metadata, using a daily-scheduled Airflow pipeline that simulates new data arriving every day.

**Note that reaching high quality / training the best possible model is not the goal of this project. The project goal is to show how airflow pipelines work, and what for we need them**

**Dataset:** `data/amazon.csv` — 1465 Amazon product listings with reviews, prices, discount percentages, and ratings.

**Pipeline stages:**

1. **Preprocess** — strip currency/percent symbols from numeric columns, extract the top-level product category, concatenate `review_title + review_content + about_product` into one text blob, then clean it (lowercase → remove URLs/special chars → remove stopwords → lemmatize)
2. **Vectorize** — TF-IDF (10k vocab, unigrams + bigrams) followed by SVD (50 components). Fitted once on the initial training set and frozen for all future runs so the feature space stays stable
3. **Train** — CatBoost regression on SVD components + 4 numeric features + `main_category` as a native categorical feature; early stopping on the validation set
4. **Evaluate** — RMSE, MAE, MAPE, R² on the test set; compared against a naive baseline (predict training mean) and the previous day's model

**Data simulation:** the dataset is treated as if only 80% of rows exist on day 0, with 2% more arriving each day. The pipeline detects how many models have already been trained to determine the current data fraction, so the simulation works regardless of actual calendar dates.

---

### How to run

#### Option 1 — local smoke test (no Docker required)

```bash
cd airflow
pip install -r requirements.txt
python src/main.py
```

Runs two full pipeline cycles (init + one daily step) and writes all artifacts to `airflow/artifacts/`. Mainly to check that the pipeline runs without errors / do debugging

#### Option 2 — full Airflow pipeline (Docker)

```bash
cd airflow
docker compose up --build -d   # first build takes a few minutes
```

Open **http://localhost:8080** (login), then:

1. Trigger `init_pipeline` manually (▶ button) — fits the vectorizer, trains the first model
2. `daily_pipeline` runs automatically every day at midnight UTC, or trigger it manually to simulate additional days

```bash
# View scheduler logs
docker compose logs -f airflow-scheduler

# Tear down (keeps artifacts)
docker compose down

# Tear down + reset all Airflow state
docker compose down -v
```

**Check AIRFLOW.md to find out more about the airflow framework**

**Also check the CREATE_docker-compose.md to figure out how to initialize the docker-compose.yaml file for the airflow-based pipelines**
