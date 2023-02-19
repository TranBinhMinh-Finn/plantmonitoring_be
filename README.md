# Plant monitoring backend

## Backend Requirements

* Docker
* Docker Compose
* Python (for dev)

## Run the backend with Docker:

Simply:
```bash
docker-compose build
docker-compose up -d 
```

## Starting the backend server (for backend development)
* Start with Docker Compose:

```bash
docker-compose build db
docker-compose up -d db adminer
```

* Create and activate a virtual environment (Windows):
```bash
python -m venv venv
venv/scripts/activate
```
On Linux:
```bash
python -m venv venv
source venv/bin/activate
```

* Now install python requirements with poetry:

```bash
pip install poetry
poetry install
```

* Then start the django server:
```bash
cd plantmonitoring_be
python manage.py runserver
```