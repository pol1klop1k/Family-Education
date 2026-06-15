from django.db import models

from registration.models import Child, School

# Create your models here.
class AccountingList(models.Model):
    """Лист учета успеваемости.
    """
    creating_date = models.DateTimeField("Время создания", auto_now_add=True)
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        verbose_name="Обучающийся",
        related_name="accounting",
    )
    is_successed = models.BooleanField("Аттестован")
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        verbose_name="Школа",
        related_name="accounting",
    )
    grade = models.IntegerField("Класс")
    study_year = models.CharField("Учебный год", max_length=9)
    mail_link = models.URLField("Диалог с родителем", blank=True)
