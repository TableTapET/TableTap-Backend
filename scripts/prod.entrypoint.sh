#!/bin/sh

set -e

echo "Applying migrations..."
python manage.py migrate

export DJANGO_SETTINGS_MODULE=tableTapBackend.settings.prod

echo "Starting Django in PRODUCTION mode..."
python manage.py runserver