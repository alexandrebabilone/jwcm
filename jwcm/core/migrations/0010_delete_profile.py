# Generated by Django 4.0.1 on 2022-04-09 01:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_delete_publicassignment_delete_speech'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]