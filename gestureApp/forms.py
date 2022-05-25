from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


# Useful for code validation in views.py
class ExperimentCode(forms.Form):
    code = forms.CharField(
        label="Code", required=True, max_length=4, min_length=4, strip=True
    )


class UserRegisterForm(UserCreationForm):
    """Form to generate new users"""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]
