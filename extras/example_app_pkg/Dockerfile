FROM python:3.12 AS base
LABEL authors="partho"
RUN pip3 install --upgrade python-dotenv rich
WORKDIR /app
COPY basichttp.py basichttp.py
ENTRYPOINT ["python3"]

