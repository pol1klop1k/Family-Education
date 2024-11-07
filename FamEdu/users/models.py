from django.db import models
from django.contrib.auth.models import AbstractUser
from registration.models import Employee

# Create your models here.

class User(AbstractUser, Employee):
    class Meta:
          db_table = "auth_user"
          verbose_name = "Пользователь"
          verbose_name_plural = "Пользователи"