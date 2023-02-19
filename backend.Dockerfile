FROM python:3.11
 
WORKDIR /app
COPY . /app

RUN pip install poetry==1.3.1
RUN poetry config virtualenvs.create false
RUN poetry install

WORKDIR /app/plantmonitoring_be

ENV PYTHONPATH=/app

EXPOSE 8000

ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000", "--settings", "config.docker"]

