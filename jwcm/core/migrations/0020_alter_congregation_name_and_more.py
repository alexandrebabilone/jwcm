# Generated by Django 4.0.1 on 2022-06-26 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_meeting_unique_meeting_per_congregation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='congregation',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Nome'),
        ),
        migrations.AddConstraint(
            model_name='person',
            constraint=models.UniqueConstraint(fields=('full_name', 'congregation'), name='unique_full_name_per_congregation'),
        ),
    ]
