from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

# Create your models here.
class School(models.Model):
    number = models.IntegerField()
    type = models.CharField(max_length=3, choices=[
        ("MUN", "Муниципалитет"), 
        ("ON", "Онлайн")
    ])
    city = models.CharField(max_length=32)

class Employee(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    patronymic = models.CharField(max_length=32)
    position = models.CharField(max_length=32, choices=[
        ("VDS", "Ведущий специалист")
    ])

class Parent(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    patronymic = models.CharField(max_length=32)
    registration_address = models.CharField(max_length=128)
    living_address = models.CharField(max_length=128)
    phone = models.CharField(validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона"),
    ])
    email = models.EmailField()

class Child(models.Model):
    name = models.CharField(max_length=32)
    surname = models.CharField(max_length=32)
    patronymic = models.CharField(max_length=32)
    birthday = models.DateField()
    registration_address = models.CharField(max_length=128)
    living_address = models.CharField(max_length=128)
    phone = models.CharField(validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона")
    ])

class Notification(models.Model):
    date = models.DateField(auto_now_add=True)
    applicant = models.ForeignKey(Parent, on_delete=models.SET_DEFAULT, default=1, related_name="notification_applicant")
    representative = models.ForeignKey(Parent, on_delete=models.SET_DEFAULT, default=1, related_name="notification_representative")
    student = models.ForeignKey(Child, on_delete=models.SET_DEFAULT, default=1, related_name="notifications")
    grade = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(11),
    ])
    prev_school = models.ForeignKey(School, on_delete=models.SET_DEFAULT, default=1, related_name="notification_prev_school")
    cur_school = models.ForeignKey(School, on_delete=models.SET_DEFAULT, default=1, related_name="notification_cur_school")
    note = models.TextField(blank=True)

"""
Возможные изменения

class ChildCard(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    grade = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(11),
    ])
    prev_school = models.ForeignKey(School, on_delete=models.SET_DEFAULT, default=1)
    cur_school = models.ForeignKey(School, on_delete=models.SET_DEFAULT, default=1)

class ParentCard(models.Model):
    requirer = models.ForeignKey(Parent, on_delete=models.CASCADE)
    accepter = models.ForeignKey(Parent, on_delete=models.SET_DEFAULT, default=1)
    aggrement = models.CharField(max_length=3, choices=[
        ("YES", "Да"),
        ("NO", "Нет"),
    ])
"""