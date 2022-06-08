# Generated by Django 4.0.4 on 2022-06-08 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestureApp', '0037_alter_experiment_group_alter_experiment_study'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='instructions',
            field=models.TextField(default='        Enter the sequence of characters in order when it appears on the screen\n        Try to do it as fast and correctly as you can\n        Do not change window or tab, or the experiment will restart\n        Make sure you only use one finger for each key\n        After clicking on "Start Experiment", and before each block, you MAY hear an auditory cue\n        Click on "Start Experiment" when you\'re ready to begin'),
        ),
    ]
