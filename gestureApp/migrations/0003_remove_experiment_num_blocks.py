# Generated by Django 3.1 on 2020-08-28 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0002_auto_20200828_1108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experiment',
            name='num_blocks',
        ),
    ]
