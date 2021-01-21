from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Experiment, Block
from django.forms import formset_factory


class ExperimentCode(forms.Form):
    code = forms.CharField(
        label="Code", required=True, max_length=4, min_length=4, strip=True
    )


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ExperimentForm(forms.ModelForm):
    class Meta:
        model = Experiment
        fields = ["name"]
