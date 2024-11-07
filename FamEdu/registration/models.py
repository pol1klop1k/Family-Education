from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator

# Create your models here.
class Person(models.Model):
    surname = models.CharField(max_length=32, verbose_name='Фамилия')
    name = models.CharField(max_length=32, verbose_name='Имя')
    patronymic = models.CharField(max_length=32, verbose_name='Отчество')

    def __str__(self):
         return f"{self.surname} {self.name} {self.patronymic}"
    
    def credentials(self):
        return f"{self.surname} {self.name[0]}.{self.patronymic[0]}."

    class Meta:
        abstract = True
        ordering = ['surname', 'name', 'patronymic']



class School(models.Model):
    number = models.IntegerField(verbose_name='Номер')
    type = models.CharField(max_length=3, verbose_name='Тип', choices=[
        ("MUN", "Муниципалитет"), 
        ("ON", "Онлайн")
    ])
    city = models.CharField(max_length=32, verbose_name='Город')

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self):
        return f'{self.city} №{self.number}'



class Employee(Person):
    position = models.CharField(max_length=32, verbose_name="Должность", choices=[
        ("VDS", "Ведущий специалист")
    ])

    class Meta(Person.Meta):
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"



class Parent(Person):
    registration_address = models.CharField(max_length=128, verbose_name='Адрес регистрации')
    living_address = models.CharField(max_length=128, verbose_name='Адрес проживания')
    phone = models.CharField(verbose_name='Телефон', validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона"),
    ])
    email = models.EmailField(verbose_name='Эл. почта')

    class Meta(Person.Meta):
        verbose_name = "Родитель"
        verbose_name_plural = "Родители"



class Child(Person):
    birthday = models.DateField(verbose_name='Дата рождения')
    registration_address = models.CharField(max_length=128, verbose_name='Адрес регистрации')
    living_address = models.CharField(max_length=128, verbose_name='Адрес проживания')
    phone = models.CharField(verbose_name='Телефон', validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона")
    ])      

    class Meta(Person.Meta):
        verbose_name = "Ребенок"
        verbose_name_plural = "Дети"


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

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

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