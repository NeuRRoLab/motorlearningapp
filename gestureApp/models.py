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

    # flag to know if the experiment should be shown or not
    published = models.BooleanField(default=False)
    published_timestamp = models.DateTimeField(null=True, default=None)
    enabled = models.BooleanField(default=True)

    # TODO: maybe get all of the practice info into a block type
    with_practice_trials = models.BooleanField(default=True)
    num_practice_trials = models.IntegerField(default=5, null=True)
    practice_is_random_seq = models.BooleanField(default=True, null=True)
    practice_seq = models.CharField(max_length=15, default="", null=True)
    practice_seq_length = models.IntegerField(default=5, null=True)
    practice_trial_time = models.FloatField(default=5, null=True)
    practice_rest_time = models.FloatField(default=5, null=True)

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

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "created_at": self.created_at,
            "creator": self.creator.username,
            "with_practice_trials": self.with_practice_trials,
            "num_practice_trials": self.num_practice_trials,
            "practice_is_random_seq": self.practice_is_random_seq,
            "practice_seq": self.practice_seq,
            "practice_seq_length": self.practice_seq_length,
            "practice_trial_time": self.practice_trial_time,
            "practice_rest_time": self.practice_rest_time,
        }


class Block(models.Model):
    class BlockTypes(models.TextChoices):
        MAX_TIME = "max_time"
        NUM_TRIALS = "num_trials"

    experiment = models.ForeignKey(
        Experiment, related_name="blocks", on_delete=models.CASCADE
    )
    sequence = models.CharField(max_length=50)
    seq_length = models.IntegerField(null=True)
    is_random = models.BooleanField(default=False)
    # Whether or not to show the same sequence everytime
    is_fixed = models.BooleanField(default=True)

    max_time_per_trial = models.FloatField(default=5)
    resting_time = models.FloatField(default=10)

    type = models.CharField(max_length=12, choices=BlockTypes.choices)
    max_time = models.FloatField(default=None, null=True, blank=True)
    num_trials = models.IntegerField(default=None, null=True, blank=True)

    # Seconds between blocks
    sec_until_next = models.FloatField(default=0)

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
    class Meta:
        ordering = ["timestamp"]

    trial = models.ForeignKey(
        Trial, related_name="keypresses", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=1)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.value + ", " + str(self.timestamp)
