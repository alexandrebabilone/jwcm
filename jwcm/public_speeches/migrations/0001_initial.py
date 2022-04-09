# Generated by Django 4.0.1 on 2022-04-09 01:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0009_delete_publicassignment_delete_speech'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speech',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(unique=True, verbose_name='Número')),
                ('theme', models.CharField(max_length=80, verbose_name='Tema')),
            ],
            options={
                'verbose_name': 'discurso',
                'verbose_name_plural': 'discursos',
            },
        ),
        migrations.CreateModel(
            name='PublicAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Data')),
                ('congregation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.congregation')),
                ('speaker', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.person', verbose_name='Orador')),
                ('speech', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='public_speeches.speech', verbose_name='Discurso')),
            ],
        ),
    ]
