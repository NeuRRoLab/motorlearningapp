# Generated by Django 3.1.3 on 2021-04-27 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0018_endsurvey_comp_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='with_feedback',
            field=models.BooleanField(default=True),
        ),
    ]