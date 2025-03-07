"""
ASGI config for FamEdu project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

sys.path.insert(0, str(Path(__file__).resolve().parent))

print(sys.path)
print(os.listdir())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
print(os.getenv("DJANGO_SETTINGS_MODULE"))

application = get_asgi_application()
