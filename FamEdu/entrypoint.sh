#!/bin/bash
set -e

echo "🔄Миграции..."
python manage.py migrate --noinput

echo "Создание суперюзера..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = '$DJANGO_SUPERUSER_USERNAME'
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created.")
else:
    print(f"Superuser {username} already exists.")
EOF

echo "🚀 Запуск Django runserver..."
exec python manage.py runserver 0.0.0.0:8000 "$@"