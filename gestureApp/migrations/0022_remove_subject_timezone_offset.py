# Generated by Django 3.1.3 on 2021-04-30 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0021_subject_timezone_offset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='timezone_offset',
        ),
    ]