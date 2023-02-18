# Plant monitoring backend

## Backend Requirements

* Docker
* Docker Compose

## Starting the backend server
* Start with Docker Compose:

```bash
docker-compose build
docker-compose up -d
```

* Now install python requirements with poetry:
```bash
python -m venv venv
pip install poetry
poetry install
```

* Then start the django server:
```bash
cd plantmonitoring_be
python manage.py runserver
```