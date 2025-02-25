from django.db import models, IntegrityError
import random, string
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from model_clone import CloneMixin
from django.db.models import F
from collections import defaultdict


class User(AbstractUser):
    """Main user of the application. Refers to the researcher, not the participant"""

    organization = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Subject(models.Model):
    """Participant in a given study"""

    # Random code to represent it
    code = models.CharField(max_length=16, blank=True, editable=False, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # generate random code
            self.code = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )
        success = False
        failures = 0
        # Do the process until finding a subject code that has not been created yet.
        # Very very unlikely to be run more than once
        while not success:
            try:
                super(Subject, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise Exception("Could not create a subject without collisions")
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
    """Represents the study in the database. Contains all possible properties and is linked by groups and experiments."""

    # Code to represent study
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    # If user is deleted, all studies are deleted as well
    creator = models.ForeignKey(User, models.CASCADE, related_name="studies")
    description = models.TextField(null=True, default="")

    # Study properties
    published = models.BooleanField(default=False)
    published_timestamp = models.DateTimeField(blank=True, null=True, default=None)
    enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
        success = False
        failures = 0
        # Run until code with no collisions is found
        while not success:
            try:
                super(Study, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise Exception("Could not create study code without collisions")
                else:
                    # looks like a collision, try another random value
                    self.code = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=4)
                    )
            else:
                success = True

    def to_dict(self):
        """Helper method to convert study to a dict to be readable from an HTML template

        Returns:
            dict: study dict with all the necessary fields
        """
        # Get all experiments from this study
        experiments = list(self.experiments.order_by("created_at").values())
        # Get all groups
        groups = list(self.groups.values())
        # get all subjects, and get specific data from them
        subjects = list(
            Subject.objects.filter(trials__block__experiment__in=self.experiments.all())
            .annotate(exp_code=F("trials__block__experiment__code"))
            .annotate(done_at=F("trials__started_at"))
            .annotate(published=F("trials__block__experiment__published"))
            .annotate(published_at=F("trials__block__experiment__published_timestamp"))
            .values()
        )
        # If the study is published, get all subjects that did the experiment after the publish date
        # Else, get all subjects
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
            # Replace group id by a group dict
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

        # Final study dictionary
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
    """Represents a group in the database"""

    # 4 character code to represent it
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    # If study is deleted all the groups in it get deleted as well
    study = models.ForeignKey(Study, on_delete=models.CASCADE, related_name="groups")
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="study_groups")

    # Group property
    enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate code
            self.code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
            # using your function as above or anything else
        success = False
        failures = 0
        # Run until code with no collisions is found
        while not success:
            try:
                super(Group, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
                    raise Exception("Could not create group code without collisions")
                else:
                    # looks like a collision, try another random value
                    self.code = "".join(
                        random.choices(string.ascii_uppercase + string.digits, k=4)
                    )
            else:
                success = True

    def to_dict(self):
        """Helper method to export group to a dictionary

        Returns:
            dict: group dictionary
        """
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
    """Represents an experiment in the database. An experiment contains multiple blocks"""

    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, models.CASCADE, related_name="experiments")
    # If a study is deleted, all related experiments are deleted
    study = models.ForeignKey(
        Study, models.CASCADE, related_name="experiments", null=False
    )
    # If a group is deleted, all related experiments are deleted
    group = models.ForeignKey(
        Group, models.CASCADE, related_name="experiments", null=False
    )

    # Experiments properties
    published = models.BooleanField(default=False)
    published_timestamp = models.DateTimeField(blank=True, null=True, default=None)
    enabled = models.BooleanField(default=True)

    # TODO: maybe get all of the practice info into a type object or something
    with_practice_trials = models.BooleanField(default=True)
    num_practice_trials = models.IntegerField(default=5, null=True, blank=True)
    practice_is_random_seq = models.BooleanField(default=True, null=True, blank=True)
    practice_seq = models.CharField(max_length=15, default="", null=True, blank=True)
    practice_seq_length = models.IntegerField(default=5, null=True, blank=True)
    practice_trial_time = models.FloatField(default=5, null=True, blank=True)
    practice_rest_time = models.FloatField(default=5, null=True, blank=True)
    rest_after_practice = models.FloatField(default=0, null=True, blank=True)

    # Experiment requirements
    requirements = models.TextField()
    # Instructions
    instructions = models.TextField(
        default="""\
        Enter the sequence of characters in order when it appears on the screen
        Try to do it as fast and correctly as you can
        Do not change window or tab, or the experiment will restart
        Make sure you only use one finger for each key
        After clicking on "Start Experiment", and before each block, you MAY hear an auditory cue
        Click on "Start Experiment" when you're ready to begin"""
    )
    # For the trials
    with_feedback = models.BooleanField(default=True)
    # For the blocks
    with_feedback_blocks = models.BooleanField(default=True)
    # Whether to show instructions during experiment
    with_shown_instructions = models.BooleanField(default=True)

    # To be able to clone the blocks when cloning the experiment
    _clone_m2o_or_o2m_fields = ["blocks"]

    def save(self, *args, **kwargs):
        # Generate random code
        if not self.code:
            self.code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=4)
            )
        success = False
        failures = 0
        # Do until no collisions are found
        while not success:
            try:
                super(Experiment, self).save(*args, **kwargs)
            except IntegrityError:
                failures += 1
                if failures > 5:
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
        """Return the number of people that have performed the experiment"""

        # If the experiment is published, return the number of people that have responded to the experiment since its publishing timestamp
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
            # Else, return all subjects who have done the experiment
            return (
                Subject.objects.filter(trials__block__experiment=self)
                .distinct()
                .count()
            )

    def has_done_experiment(self, subject):
        """Returns whether the subject has performed this experiment or not"""
        return self.blocks.filter(trials__subject=subject).exists()

    def to_dict(self):
        """Helper method to transform experiment to dictionary

        Returns:
            dict: experiment dictionary
        """
        study_code = self.study.code
        study_name = self.study.name
        group = {"code": self.group.code, "name": self.group.name}

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
            "with_shown_instructions": self.with_shown_instructions,
            "rest_after_practice": self.rest_after_practice,
            "requirements": self.requirements,
            "instructions": self.instructions,
            "enabled": self.enabled,
            "responses": self.num_responses(),
        }


class Block(CloneMixin, models.Model):
    """Represents a single block in an experiment in the database"""

    class BlockTypes(models.TextChoices):
        """Types the block can be"""

        MAX_TIME = "max_time"
        NUM_TRIALS = "num_trials"

    # If parent experiment deleted, all blocks are deleted as well.
    experiment = models.ForeignKey(
        Experiment, related_name="blocks", on_delete=models.CASCADE
    )
    # Sequence of this block
    sequence = models.CharField(max_length=50)
    seq_length = models.IntegerField(null=True)
    is_random = models.BooleanField(default=False)
    # Whether or not to show the same sequence everytime
    # TODO: not being used currently
    is_fixed = models.BooleanField(default=True)
    # Hand to show in instructions
    hand_to_use = models.CharField(max_length=30, default="right")

    max_time_per_trial = models.FloatField(default=5)
    # Resting time between trials
    resting_time = models.FloatField(default=10)

    type = models.CharField(max_length=12, choices=BlockTypes.choices)
    max_time = models.FloatField(default=None, null=True, blank=True)
    num_trials = models.IntegerField(default=None, null=True, blank=True)

    # Seconds between blocks
    sec_until_next = models.FloatField(default=0)

    def clean(self):
        """Validation method for the block properties"""
        # More checks can be added
        if self.type == Block.BlockTypes.MAX_TIME and self.max_time is None:
            raise ValidationError("Block type is of max time, but no max time supplied")
        elif self.type == Block.BlockTypes.NUM_TRIALS and self.num_trials is None:
            raise ValidationError(
                "Block type is of num trials, but num trials not supplied"
            )


class Trial(models.Model):
    """Represents a trial completed by a subject in the database database"""

    # If the corresponding block is deleted, all associated trials should be deleted as well
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="trials")
    # Prevent deletion if the corresponding subject is deleted
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
    """Represents a keypress in the database. A trial is composed of multiple keypresses"""

    class Meta:
        ordering = ["timestamp"]

    # Delete keypresses if the trial is deleted
    trial = models.ForeignKey(
        Trial, related_name="keypresses", on_delete=models.CASCADE
    )
    # Which key was pressed
    value = models.CharField(max_length=1)
    timestamp = models.DateTimeField()

    def __str__(self):
        return self.value + ", " + str(self.timestamp)


class EndSurvey(models.Model):
    """Represents the full end survey in the database"""

    # Potentially could be saved in a NoSQL database for simplicity
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    # Set subject field to null if corresponding subject is deleted
    subject = models.ForeignKey(
        Subject, on_delete=models.SET_NULL, null=True, related_name="surveys"
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

