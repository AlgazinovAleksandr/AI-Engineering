FROM apache/airflow:2.9.3

# gcc/g++ are required to compile some Python extension packages (e.g. catboost wheels)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Always install pip packages as the 'airflow' user, not root
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Bake NLTK corpora into the image so tasks don't download at runtime
RUN python -c "\
import nltk; \
nltk.download('stopwords', quiet=True); \
nltk.download('wordnet', quiet=True); \
nltk.download('omw-1.4', quiet=True); \
"
