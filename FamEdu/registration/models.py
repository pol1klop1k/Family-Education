from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=32, verbose_name='Имя')
    surname = models.CharField(max_length=32, verbose_name='Фамилия')
    patronymic = models.CharField(max_length=32, verbose_name='Отчество')

    def __str__(self):
         return f"{self.surname} {self.name} {self.patronymic}"

    class Meta:
        abstract = True



class School(models.Model):
    number = models.IntegerField(verbose_name='Номер')
    type = models.CharField(max_length=3, verbose_name='Тип', choices=[
        ("MUN", "Муниципалитет"), 
        ("ON", "Онлайн")
    ])
    city = models.CharField(max_length=32, verbose_name='Город')

    def __str__(self):
        return f'{self.city},{self.number}'



class Employee(Person):
    position = models.CharField(max_length=32, choices=[
        ("VDS", "Ведущий специалист")
    ])



class Parent(Person):
    registration_address = models.CharField(max_length=128, verbose_name='Адрес регистрации')
    living_address = models.CharField(max_length=128, verbose_name='Адрес проживания')
    phone = models.CharField(verbose_name='Телефон', validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона"),
    ])
    email = models.EmailField(verbose_name='Эл. почта')



class Child(Person):
    birthday = models.DateField(verbose_name='Дата рождения')
    registration_address = models.CharField(max_length=128, verbose_name='Адрес регистрации')
    living_address = models.CharField(max_length=128, verbose_name='Адрес проживания')
    phone = models.CharField(verbose_name='Телефон', validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона")
    ])      



class Notification(models.Model):
    date = models.DateField(auto_now_add=True)
    applicant = models.ForeignKey(Parent, on_delete=models.RESTRICT, related_name="notification_applicant", verbose_name='Заявитель')
    representative = models.ForeignKey(Parent, on_delete=models.RESTRICT, related_name="notification_representative", verbose_name='Второй представитель')
    student = models.ForeignKey(Child, on_delete=models.RESTRICT, related_name="notifications", verbose_name='Обучающийся')
    grade = models.IntegerField(verbose_name='Класс', validators=[
        MinValueValidator(1),
        MaxValueValidator(11),
    ])
    prev_school = models.ForeignKey(School, on_delete=models.RESTRICT, related_name="notification_prev_school", verbose_name='Предыдущая школа')
    cur_school = models.ForeignKey(School, on_delete=models.RESTRICT, related_name="notification_cur_school", verbose_name='Школа прикрепления')
    note = models.TextField(blank=True, verbose_name='Замечание')

    def __str__(self):
        return f'Уведомление №{self.pk} от {self.date}'

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