# Generated by Django 4.0.1 on 2022-06-26 23:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_delete_part'),
        ('life_and_ministry', '0005_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='part',
            options={'verbose_name': 'parte', 'verbose_name_plural': 'partes'},
        ),
        migrations.RemoveField(
            model_name='part',
            name='assistant',
        ),
        migrations.RemoveField(
            model_name='part',
            name='meeting',
        ),
        migrations.RemoveField(
            model_name='part',
            name='owner',
        ),
        migrations.CreateModel(
            name='LifeAndMinistryAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assistant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='helper', to='core.person', verbose_name='Ajudante')),
                ('meeting', models.ManyToManyField(to='core.Meeting', verbose_name='Reunião')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='owner', to='core.person', verbose_name='Dono da parte')),
                ('part', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='life_and_ministry.part', verbose_name='Parte')),
            ],
            options={
                'verbose_name': 'Designação da reunião Vida e Ministério',
                'verbose_name_plural': 'Designações da reunião Vida e Ministério',
            },
        ),
    ]
