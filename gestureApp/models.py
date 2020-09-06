from django.db import models, IntegrityError
import random, string
from django.utils import timezone

# Create your models here.
class Sequence(models.Model):
    sequence = models.CharField(max_length=15)

    def __str__(self):
        return self.sequence

class Designer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    organization = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    


class Subject(models.Model):
    code = models.CharField(max_length=16, blank=True, editable=False, primary_key=True)
    age = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            # using your function as above or anything else
        success = False
        failures = 0
        while not success:
            try:
                super(Subject, self).save(*args, **kwargs)
            except IntegrityError:
                 failures += 1
                 if failures > 5: # or some other arbitrary cutoff point at which things are clearly wrong
                     raise
                 else:
                     # looks like a collision, try another random value
                     self.code = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            else:
                 success = True
    def __str__(self):
        return self.code

class Experiment(models.Model):
    code = models.CharField(max_length=4, blank=True, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(Designer, models.SET_NULL, null=True)
    resting_time = models.IntegerField(default=10)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            # using your function as above or anything else
        success = False
        failures = 0
        while not success:
            try:
                super(Experiment, self).save(*args, **kwargs)
            except IntegrityError:
                 failures += 1
                 if failures > 5: # or some other arbitrary cutoff point at which things are clearly wrong
                     raise
                 else:
                     # looks like a collision, try another random value
                     self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            else:
                 success = True
    
    def __str__(self):
        return self.code + ' | ' + self.name

class Block(models.Model):
    experiment = models.ForeignKey(Experiment, related_name='blocks', on_delete=models.CASCADE)
    sequence = models.ForeignKey(Sequence, on_delete=models.PROTECT)
    time_per_trial = models.IntegerField()
    num_trials = models.IntegerField(default=10)


class Trial(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    started_at = models.DateTimeField()
    did_timeout = models.BooleanField(default=False)
    input_sequence = models.CharField(max_length=50)
    time = models.FloatField(null=True)

    def __str__(self):
        return str(timezone.localtime(self.started_at)) + ' | ' + str(self.time) + 's'

    def is_correct(self):
        if self.block.sequence.sequence == self.input_sequence:
            return True
        return False
