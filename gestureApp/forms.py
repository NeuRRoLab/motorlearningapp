from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Experiment, Block
from django.forms import formset_factory, inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit
from .block_formset import Formset


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
        exclude = ["creator", "created_at", "code", "published"]

    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3 create-label"
        self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(
                Field("name"),
                Fieldset("Add blocks", Formset("blocks")),
                HTML("<br>"),
                ButtonHolder(Submit("submit", "save")),
            )
        )


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = ["sequence"]

    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        # self.helper.form_class = "form-horizontal"
        # self.helper.label_class = "col-md-3 create-label"
        # self.helper.field_class = "col-md-9"
        self.helper.layout = Layout(
            Div(
                Field("sequence"),
                Field("seq_length"),
                HTML("<br>"),
                ButtonHolder(Submit("submit", "save")),
            )
        )


BlockFormSet = inlineformset_factory(
    Experiment, Block, form=BlockForm, extra=1, can_delete=True
)
