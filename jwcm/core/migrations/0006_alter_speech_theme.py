# Generated by Django 4.0.1 on 2022-03-08 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_publicassignment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speech',
            name='theme',
            field=models.CharField(max_length=80, verbose_name='Tema'),
        ),
    ]
