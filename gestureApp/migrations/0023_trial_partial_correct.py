# Generated by Django 3.1.3 on 2021-05-04 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0022_remove_subject_timezone_offset'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='partial_correct',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]