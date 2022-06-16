# Generated by Django 4.0.1 on 2022-06-16 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('public_speeches', '0004_alter_weekendmeeting_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='congregation',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='indicator_1',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='indicator_2',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='mic_1',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='mic_2',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='note_sound_table',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='president',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='public_speech',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='reader_watchtower',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='ruling_watchtower',
        ),
        migrations.RemoveField(
            model_name='weekendmeeting',
            name='zoom_indicator',
        ),
        migrations.DeleteModel(
            name='PublicAssignment',
        ),
        migrations.DeleteModel(
            name='WeekendMeeting',
        ),
    ]
