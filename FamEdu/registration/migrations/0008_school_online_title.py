# Generated by Django 5.1.1 on 2024-12-06 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_alter_school_number_alter_school_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='online_title',
            field=models.CharField(blank=True, max_length=64, verbose_name='Название'),
        ),
    ]
