#!/bin/sh
set -e

echo "Applying migrations..."
python manage.py migrate

export DJANGO_SETTINGS_MODULE=config.settings.dev

echo "Starting Django in DEVELOPMENT mode..."
python manage.py runserver