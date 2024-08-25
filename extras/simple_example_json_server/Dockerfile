FROM python:3.12 AS base
LABEL authors="partho"

WORKDIR /app
RUN python3 -m venv .venv
COPY requirements.txt .
COPY simplejsonserver/basichttp.py basichttp.py
RUN /app/.venv/bin/pip install -r requirements.txt
ENTRYPOINT ["/app/.venv/bin/python3", "basichttp.py"]
