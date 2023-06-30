#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing the latest version of poetry..."

pip install --upgrade pip
pip install celery
pip install djangorestframework
pip install django-celery-beat
# pip install redis
pip install yagmail
pip install python-dotenv
pip install poetry==1.2.0
pip install authlib
rm poetry.lock

poetry lock

python -m poetry install


python manage.py collectstatic --no-input
python manage.py migrate


