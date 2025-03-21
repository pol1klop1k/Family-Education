# Generated by Django 5.1.1 on 2024-11-29 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_notification_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='position',
            field=models.CharField(choices=[('Ведущий специалист', 'Ведущий специалист')], max_length=32, verbose_name='Должность'),
        ),
        migrations.AlterField(
            model_name='school',
            name='type',
            field=models.CharField(choices=[('Муниципалитет', 'Муниципалитет'), ('Онлайн', 'Онлайн')], max_length=13, verbose_name='Тип'),
        ),
    ]
