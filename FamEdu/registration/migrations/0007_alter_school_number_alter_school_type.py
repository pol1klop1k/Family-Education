# Generated by Django 5.1.1 on 2024-12-06 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_alter_school_city_alter_school_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Номер'),
        ),
        migrations.AlterField(
            model_name='school',
            name='type',
            field=models.CharField(choices=[('Муниципалитет', 'Муниципалитет'), ('Онлайн', 'Онлайн')], max_length=13, verbose_name='Тип'),
        ),
    ]
