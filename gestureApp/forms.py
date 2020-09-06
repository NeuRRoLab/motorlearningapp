from django import forms

class ExperimentCode(forms.Form):
    code = forms.CharField(label='Code',required=True,max_length=4,min_length=4,strip=True)