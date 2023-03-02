FROM python:3.11

WORKDIR /app
COPY . /app

RUN pip install poetry==1.3.1 --no-cache
RUN poetry config virtualenvs.create false
RUN poetry install  --no-dev --no-root

WORKDIR /app/plantmonitoring_be

ENV PYTHONPATH=/app

