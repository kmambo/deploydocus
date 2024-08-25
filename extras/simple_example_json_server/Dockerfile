FROM python:3.12 AS base
LABEL authors="partho"

WORKDIR /app
RUN python3 -m venv .venv
RUN . .venv/bin/activate
COPY requirements.txt .
COPY simplejsonserver/basichttp.py basichttp.py
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3", "basichttp.py"]
