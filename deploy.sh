#!/bin/bash

cd /home/yamato/Django_CICD/stocks_products
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
sudo systemclt restart gunicorn
