import json
from datetime import datetime
from urllib import parse
import random, string

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, now
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.forms import inlineformset_factory

from django.forms.models import model_to_dict
from django.db.models import F

from .forms import ExperimentCode, UserRegisterForm
from .models import Experiment, Subject, Trial, User, Keypress, Block


@method_decorator([login_required], name="dispatch")
class Profile(DetailView):
    model = User
    template_name = "gestureApp/profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["experiments"] = self.request.user.experiments.all()
        return context


class SignUpView(CreateView):
    template_name = "gestureApp/register.html"
    success_url = reverse_lazy("gestureApp:profile")
    form_class = UserRegisterForm


def preparation_screen(request):
    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code)
        return render(request, "gestureApp/prep_screen.html", {"exp_code": code},)
    else:
        form = ExperimentCode()
        return render(
            request,
            "gestureApp/home.html",
            {"form": form, "error_message": "Form invalid"},
        )


# Create your views here.
def experiment(request):
    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code)
        return render(
            request,
            "gestureApp/experiment.html",
            {
                "experiment": experiment.to_dict(),
                "blocks": list(experiment.blocks.all().values()),
            },
        )
    else:
        form = ExperimentCode()
        return render(
            request,
            "gestureApp/home.html",
            {"form": form, "error_message": "Form invalid"},
        )


def home(request):
    form = ExperimentCode()
    return render(request, "gestureApp/home.html", {"form": form})


def create_trials(request):
    data = json.loads(request.body)
    exp_code = data.get("experiment")
    print(exp_code, type(exp_code))
    experiment = get_object_or_404(Experiment, pk=exp_code)

    # Create a new subject
    subject = Subject(age=25)
    subject.save()
    # Save the trials to database.
    experiment_trials = json.loads(data.get("experiment_trials"))
    print(experiment_trials)
    for i, block in enumerate(experiment_trials):
        for trial in block:
            t = Trial(
                block=experiment.blocks.all()[i],
                subject=subject,
                started_at=make_aware(
                    datetime.fromtimestamp(trial["started_at"] / 1000)
                ),
                correct=trial["correct"],
            )
            t.save()
            for keypress in trial["keypresses"]:
                value = keypress["value"]
                timestamp = keypress["timestamp"]
                keypress = Keypress(
                    trial=t,
                    value=value,
                    timestamp=make_aware(datetime.fromtimestamp(timestamp / 1000)),
                )
                keypress.save()

    # Create response
    data = {}
    return JsonResponse(data)


@login_required
def create_experiment(request):
    if request.method == "POST":
        exp_info = json.loads(request.body)
        exp_practice_seq = exp_info["practice_seq"]
        if exp_info["with_practice_trials"] and exp_info["practice_is_random_seq"]:
            exp_practice_seq = "".join(
                random.choices(string.digits, k=exp_info["practice_seq_length"])
            )
        experiment = Experiment.objects.create(
            name=exp_info["name"],
            creator=request.user,
            with_practice_trials=exp_info["with_practice_trials"],
            num_practice_trials=exp_info["practice_trials"],
            practice_is_random_seq=exp_info["practice_is_random_seq"],
            practice_seq=exp_practice_seq,
            practice_seq_length=len(exp_practice_seq),
            practice_trial_time=exp_info["practice_trial_time"],
            practice_rest_time=exp_info["practice_rest_time"],
        )
        for block in exp_info["blocks"]:
            print("hola")
            print(block)
            sequence = block["sequence"]
            if block["is_random_sequence"]:
                sequence = "".join(random.choices(string.digits, k=block["seq_length"]))
            block_obj = Block(
                experiment=experiment,
                sequence=sequence,
                seq_length=len(sequence),
                is_random=block["is_random_sequence"],
                max_time_per_trial=block["max_time_per_trial"],
                resting_time=block["resting_time"],
                type=Block.BlockTypes(block["block_type"]),
                max_time=block["max_time"],
                num_trials=block["num_trials"],
                sec_until_next=block["sec_until_next"],
            )
            block_obj.full_clean()
            block_obj.save()
    return render(request, "gestureApp/create_experiment.html", {})


@login_required
def download_raw_data(request):
    from djqscsv import render_to_csv_response

    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        qs = Experiment.objects.filter(pk=code).values(
            experiment_code=F("code"),
            subject_code=F("blocks__trials__subject__code"),
            block_id=F("blocks"),
            block_sequence=F("blocks__sequence"),
            trial_id=F("blocks__trials__id"),
            correct_input=F("blocks__trials__correct"),
            keypress_timestamp=F("blocks__trials__keypresses__timestamp"),
            keypress_value=F("blocks__trials__keypresses__value"),
        )
        return render_to_csv_response(qs, filename="experiment_" + code + ".csv")


@login_required
def download_processed_data(request):
    from djqscsv import render_to_csv_response

    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        # In the processed data, there should be:
        #   Number of correct sequences in each block
        #   Execution time for each of the correct sequences
        #   Block type
        #   Subject code
        #   Block code
        qs = Experiment.objects.filter(pk=code).values(
            experiment_code=F("code"),
            subject_code=F("blocks__trials__subject__code"),
            block_id=F("blocks"),
            block_sequence=F("blocks__sequence"),
            # Block type
            # Number of correct trials
            # Average execution time
        )
        return render_to_csv_response(qs, filename="experiment_" + code + ".csv")


def current_user(request):
    if request.method == "GET":
        if request.user.is_anonymous:
            return JsonResponse({})

        user = model_to_dict(
            request.user, fields=["first_name", "last_name", "username", "email"]
        )
        return JsonResponse(user)


@login_required
def user_experiments(request):
    if request.method == "GET":
        exp_array = []
        for experiment in request.user.experiments.all():
            exp_obj = {}
            exp_obj["code"] = experiment.code
            exp_obj["name"] = experiment.name
            exp_obj["responses"] = (
                Subject.objects.filter(trials__block__experiment=experiment)
                .distinct()
                .count()
            )
            exp_array.append(exp_obj)
        return JsonResponse({"experiments": exp_array})
