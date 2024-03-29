# Generated by Django 4.0.1 on 2022-11-29 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_remove_congregation_lpw_and_more'),
        ('lpw', '0002_congregationavailability_monthlpw_personavailability_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('morning_available', models.BooleanField(default=False, verbose_name='Manhã disponível')),
                ('afternoon_available', models.BooleanField(default=False, verbose_name='Tarde disponível')),
                ('night_available', models.BooleanField(default=False, verbose_name='Noite disponível')),
                ('date', models.DateField(verbose_name='Data')),
                ('afternoon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.person')),
                ('congregation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.congregation')),
                ('morning', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.person')),
                ('night', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.person')),
            ],
        ),
        migrations.DeleteModel(
            name='MonthLPW',
        ),
    ]
