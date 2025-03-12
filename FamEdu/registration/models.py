from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.urls import reverse

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
    name = models.CharField(max_length=32, verbose_name="Тип образовательного учреждения", blank=True, choices=[
        ("МБОУ СОШ", "МБОУ СОШ"),
        ("ГБОУ СОШ", "ГБОУ СОШ"),
    ])
    number = models.IntegerField(verbose_name='Номер', blank=True, null=True)
    type = models.CharField(max_length=13, verbose_name='Тип', choices=[
        ("Муниципалитет", "Муниципалитет"), 
        ("Онлайн", "Онлайн")
    ])
    city = models.CharField(max_length=32, verbose_name='Город', blank=True)
    online_title = models.CharField(max_length=64, verbose_name="Название", blank=True)

    class Meta:
        verbose_name = "Школа"
        verbose_name_plural = "Школы"

    def __str__(self):
        if self.type == "Муниципалитет":
            return f'{self.name} №{self.number} г.{self.city}'
        return f'{self.online_title}'
    
    def title(self):
        return self.__str__()

    def get_absolute_url(self):
        return reverse("registration:directory_update", kwargs={"pk": self.pk, "entity": "school"})


class Employee(Person):
    position = models.CharField(max_length=32, verbose_name="Должность", choices=[
        ("Ведущий специалист", "Ведущий специалист")
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
        verbose_name = "Заявитель"
        verbose_name_plural = "Заявители"

    def get_absolute_url(self):
        return reverse("registration:directory_update", kwargs={"entity": "applicant", "pk": self.pk})



class Child(Person):
    birthday = models.DateField(verbose_name='Дата рождения')
    registration_address = models.CharField(max_length=128, verbose_name='Адрес регистрации')
    living_address = models.CharField(max_length=128, verbose_name='Адрес проживания')
    phone = models.CharField(verbose_name='Телефон', validators=[
        RegexValidator(regex=r"\+7\d{10}", message="Введите корректный номер телефона")
    ])      

    class Meta(Person.Meta):
        verbose_name = "Обучающийся"
        verbose_name_plural = "Обучающиеся"

    def get_absolute_url(self):
        return reverse("registration:directory_update", kwargs={"pk": self.pk, "entity": "student"})

class Notification(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name="Дата")
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
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name="notifications", verbose_name="Сотрудник")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def __str__(self):
        return f'Уведомление №{self.pk} от {self.date}'
    
    def get_absolute_url(self):
        return reverse("registration:notification_detail", kwargs={"pk": self.pk})

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