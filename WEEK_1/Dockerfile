ARG AIRFLOW_BASE_IMAGE=apache/airflow:2.10.5-python3.12
FROM ${AIRFLOW_BASE_IMAGE}

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    wget \
    vim \
    netcat-openbsd \
    postgresql-client \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
