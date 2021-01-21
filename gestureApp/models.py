from django.db import models, IntegrityError
import random, string
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    organization = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Subject(models.Model):
    code = models.CharField(max_length=16, blank=True, editable=False, primary_key=True)
    age = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )
            # using your function as above or anything else
        success = False
        failures = 0
        while not success:
            try:
                super(Subject, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if (
                    failures > 5
                ):  # or some other arbitrary cutoff point at which things are clearly wrong
                    raise
                else:
                    # looks like a collision, try another random value
                    self.code = "".join(
                        random.choices(string.ascii_letters + string.digits, k=16)
                    )
            else:
                success = True

    def __str__(self):
        return self.code


class Experiment(models.Model):
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="experiments")
    num_practice_trials = models.IntegerField(default=5)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
            # using your function as above or anything else
        success = False
        failures = 0
        while not success:
            try:
                super(Experiment, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if (
                    failures > 5
                ):  # or some other arbitrary cutoff point at which things are clearly wrong
                    raise
                else:
                    # looks like a collision, try another random value
                    self.code = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=4)
                    )
            else:
                success = True

    def __str__(self):
        return self.code + " | " + self.name


class Block(models.Model):
    class BlockTypes(models.TextChoices):
        MAX_TIME = "max_time"
        NUM_TRIALS = "num_trials"

    experiment = models.ForeignKey(
        Experiment, related_name="blocks", on_delete=models.CASCADE
    )
    sequence = models.CharField(max_length=15)
    max_time_per_trial = models.IntegerField(default=5)
    resting_time = models.IntegerField(default=10)

    type = models.CharField(max_length=12, choices=BlockTypes.choices)
    max_time = models.IntegerField(default=None, null=True, blank=True)
    num_trials = models.IntegerField(default=None, null=True, blank=True)

    def clean(self):
        if self.type == Block.BlockTypes.MAX_TIME and self.max_time is None:
            raise ValidationError("Block type is of max time, but no max time supplied")
        elif self.type == Block.BlockTypes.NUM_TRIALS and self.num_trials is None:
            raise ValidationError(
                "Block type is of num trials, but num trials not supplied"
            )


class Trial(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="trials")
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="trials"
    )
    started_at = models.DateTimeField()
    time = models.FloatField(null=True)
    correct = models.BooleanField()

    def __str__(self):
        return str(timezone.localtime(self.started_at))


class Keypress(models.Model):
    trial = models.ForeignKey(
        Trial, related_name="keypresses", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=1)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.value + ", " + str(self.timestamp)
