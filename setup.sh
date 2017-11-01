#!/bin/bash
virtualenv env
virtualenv --relocatable env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata system/fixtures/initial.json