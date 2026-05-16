#!/bin/bash
set -e

echo "🔄Миграции..."
python manage.py migrate --noinput

echo "Создание суперюзера..."
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
  python manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL
fi

echo "🚀 Запуск Django runserver..."
exec python manage.py runserver 0.0.0.0:8000 "$@"