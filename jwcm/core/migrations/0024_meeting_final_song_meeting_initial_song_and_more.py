# Generated by Django 4.0.1 on 2022-09-18 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_rename_reader_watchtower_meeting_watchtower_reader_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='final_song',
            field=models.CharField(max_length=30, null=True, verbose_name='Cântico final'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='initial_song',
            field=models.CharField(max_length=30, null=True, verbose_name='Cântico inicial'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='middle_song',
            field=models.CharField(max_length=30, null=True, verbose_name='Cântico do meio'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='week',
            field=models.CharField(max_length=30, null=True, verbose_name='Semana'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='weekly_reading',
            field=models.CharField(max_length=30, null=True, verbose_name='Leitura Semanal'),
        ),
    ]