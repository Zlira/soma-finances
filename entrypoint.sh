#!/bin/sh

echo "Waiting for mariadb..."

while ! nc -z $SQL_HOST $SQL_PORT; do
    sleep 0.1
done

echo "Mariadb started"

python manage.py migrate

exec "$@"