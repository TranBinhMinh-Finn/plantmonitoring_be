FROM mysql

ENV MYSQL_DATABASE=schema.sql \
    MYSQL_ROOT_PASSWORD=example

ADD schema.sql /docker-entrypoint-initdb.d

EXPOSE 3306