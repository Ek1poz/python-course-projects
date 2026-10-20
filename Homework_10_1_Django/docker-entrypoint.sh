#!/bin/bash

set -e

echo "Applying migrations..."
python manage.py migrate

echo "Gathering static files..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000