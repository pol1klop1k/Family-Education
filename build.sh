#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python FamEdu/manage.py collectstatic --no-input

python FamEdu/manage.py migrate

echo "builded"