from django.db import models, IntegrityError
import random, string
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from model_clone import CloneMixin
from django.db.models import F
from collections import defaultdict


class User(AbstractUser):
    organization = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Subject(models.Model):
    code = models.CharField(max_length=16, blank=True, editable=False, primary_key=True)

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


class Study(models.Model):
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="studies")
    description = models.TextField(null=True, default="")

    # flag to know if the experiment should be shown or not
    published = models.BooleanField(default=False)
    published_timestamp = models.DateTimeField(blank=True, null=True, default=None)
    enabled = models.BooleanField(default=True)

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
                super(Study, self).save(*args, **kwargs)
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

    def to_dict2(self):
        return {
            "code": self.code,
            "name": self.name,
            "groups": [
                g.to_dict() for g in self.groups.prefetch_related("experiments").all()
            ],
            "experiments": [
                e.to_dict() for e in self.experiments.order_by("created_at").all()
            ],
            "created_at": self.created_at,
            "published": self.published,
            "creator": self.creator.username,
            "description": self.description,
            "enabled": self.enabled,
        }

    def to_dict(self):
        experiments = list(self.experiments.values())
        groups = list(self.groups.values())
        subjects = list(
            Subject.objects.filter(trials__block__experiment__in=self.experiments.all())
            .annotate(exp_code=F("trials__block__experiment__code"))
            .annotate(done_at=F("trials__started_at"))
            .annotate(published=F("trials__block__experiment__published"))
            .annotate(published_at=F("trials__block__experiment__published_timestamp"))
            .values()
        )
        exp_subjects = defaultdict(set)
        for s in subjects:
            # Factor in the published or unpublished status of the experiment
            if (s["published"] and s["done_at"] > s["published_at"]) or (
                not s["published"]
            ):
                exp_subjects[s["exp_code"]].add(s["code"])

        groups_names = {}
        for g in groups:
            groups_names[g["code"]] = g["name"]
            g.pop("study_id")
            g["study"] = {"code": self.code, "name": self.name}
        creator = self.creator.username

        for e in experiments:
            # Replace group id by a group object
            group_id = e["group_id"]
            e["group"] = {"code": group_id, "name": groups_names[group_id]}
            # Replace study id by a study object
            e.pop("study_id")
            e["study"] = {"code": self.code, "name": self.name}
            # Replace creator by creator username
            e.pop("creator_id")
            e["creator"] = creator

            # Responses
            e["responses"] = len(exp_subjects[e["code"]])

        for g in groups:
            g["experiments"] = [e for e in experiments if e["group_id"] == g["code"]]

        study_dict = {
            "code": self.code,
            "name": self.name,
            "created_at": self.created_at,
            "published": self.published,
            "creator": creator,
            "description": self.description,
            "enabled": self.enabled,
            "experiments": experiments,
            "groups": groups,
        }
        return study_dict


class Group(models.Model):
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="groups")
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="study_groups")
    enabled = models.BooleanField(default=True)

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
                super(Group, self).save(*args, **kwargs)
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

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "experiments": [
                e.to_dict() for e in self.experiments.order_by("created_at").all()
            ],
            "created_at": self.created_at,
            "creator": self.creator.username,
            "enabled": self.enabled,
        }


class Experiment(CloneMixin, models.Model):
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="experiments")
    # FIXME: remove the null
    study = models.ForeignKey(
        Study, models.CASCADE, related_name="experiments", null=True
    )
    group = models.ForeignKey(
        Group, models.CASCADE, related_name="experiments", null=True
    )

    # flag to know if the experiment should be shown or not
    published = models.BooleanField(default=False)
    published_timestamp = models.DateTimeField(blank=True, null=True, default=None)
    enabled = models.BooleanField(default=True)

    # TODO: maybe get all of the practice info into a block type
    with_practice_trials = models.BooleanField(default=True)
    num_practice_trials = models.IntegerField(default=5, null=True, blank=True)
    practice_is_random_seq = models.BooleanField(default=True, null=True, blank=True)
    practice_seq = models.CharField(max_length=15, default="", null=True, blank=True)
    practice_seq_length = models.IntegerField(default=5, null=True, blank=True)
    practice_trial_time = models.FloatField(default=5, null=True, blank=True)
    practice_rest_time = models.FloatField(default=5, null=True, blank=True)
    rest_after_practice = models.FloatField(default=0, null=True, blank=True)

    # Requirements
    requirements = models.TextField()

    # For the trials
    with_feedback = models.BooleanField(default=True)
    # For the blocks
    with_feedback_blocks = models.BooleanField(default=True)

    _clone_m2o_or_o2m_fields = ["blocks"]

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

    def num_responses(self):
        if self.published:
            return (
                Subject.objects.filter(
                    trials__block__experiment=self,
                    trials__started_at__gt=self.published_timestamp,
                )
                .distinct()
                .count()
            )
        else:
            return (
                Subject.objects.filter(trials__block__experiment=self)
                .distinct()
                .count()
            )

    def has_done_experiment(self, subject):
        return self.blocks.filter(trials__subject=subject).exists()

    def to_dict(self):
        try:
            study_code = self.study.code
            study_name = self.study.name
        except AttributeError:
            study_code = None
            study_name = None
        try:
            group = {"code": self.group.code, "name": self.group.name}
        except AttributeError:
            group = None

        return {
            "code": self.code,
            "study": {"code": study_code, "name": study_name},
            "group": group,
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
            "published": self.published,
            "with_feedback": self.with_feedback,
            "with_feedback_blocks": self.with_feedback_blocks,
            "rest_after_practice": self.rest_after_practice,
            "requirements": self.requirements,
            "enabled": self.enabled,
            "responses": self.num_responses(),
        }


class Block(CloneMixin, models.Model):
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
    finished_at = models.DateTimeField()
    time = models.FloatField(null=True)
    correct = models.BooleanField()
    # If the block ended before the user could input more keypresses, but the keypresses were correct until that point
    partial_correct = models.BooleanField()

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


class EndSurvey(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    subject = models.OneToOneField(
        Subject, on_delete=models.SET_NULL, null=True, related_name="survey"
    )
    age = models.IntegerField()
    gender = models.CharField(max_length=15)
    comp_type = models.CharField(max_length=35)
    comments = models.TextField(null=True)
    medical_condition = models.BooleanField()
    hours_of_sleep = models.IntegerField()
    excercise_regularly = models.BooleanField()
    keypress_experiment_before = models.BooleanField()
    followed_instructions = models.BooleanField()
    hand_used = models.CharField(max_length=15)
    dominant_hand = models.CharField(max_length=10)
    level_education = models.CharField(max_length=50)

