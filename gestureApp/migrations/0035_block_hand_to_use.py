# Generated by Django 3.1.3 on 2021-07-01 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0034_group_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='hand_to_use',
            field=models.CharField(default='right', max_length=30),
        ),
    ]