import csv
import json
import random
import string
from datetime import datetime
from urllib import parse

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Max, Min, Q
from django.forms import inlineformset_factory
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, now
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView

from .forms import ExperimentCode, UserRegisterForm
from .models import Block, Experiment, Keypress, Subject, Trial, User


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
                "blocks": list(experiment.blocks.order_by("id").values()),
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
                block=experiment.blocks.order_by("id")[i],
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
        # When not working with sqlite, we will be able to do something like this:
        #   Trial.objects.filter(block__experiment__code="952P", block=12,subject="E7kMfKZHIZjL375d",correct=True).annotate(first_keypress=Min("keypresses__timestamp")).annotate(last_keypress=Max("keypresses__timestamp")).aggregate(avg_diff=Avg(F("first_keypress")-F("last_keypress")))
        no_et = (
            Experiment.objects.filter(pk=code)
            .values("code", "blocks", "blocks__trials__subject")
            .distinct()
            .annotate(
                num_correct_trials=Count(
                    "blocks__trials", filter=Q(blocks__trials__correct=True)
                )
            )
            .annotate(total_trials=Count("blocks__trials"))
        )
        no_et = list(no_et)
        for values_dict in no_et:
            values_dict["experiment_code"] = values_dict.pop("code")
            values_dict["block_id"] = values_dict.pop("blocks")
            values_dict["subject_code"] = values_dict.pop("blocks__trials__subject")
            values_dict["num_correct_trials"] = values_dict.pop("num_correct_trials")
            values_dict["total_trials"] = values_dict.pop("total_trials")

        for values_dict in no_et:
            # TODO: if the difference between the starting timestamp of trial and last keypress is desired, change
            qs = (
                Trial.objects.filter(
                    block__experiment__code=values_dict["experiment_code"],
                    block=values_dict["block_id"],
                    subject=values_dict["subject_code"],
                    correct=True,
                )
                .annotate(first_keypress=Min("keypresses__timestamp"))
                .annotate(last_keypress=Max("keypresses__timestamp"))
            )
            if len(qs) > 0:
                values_dict["avg_execution_time_ms"] = (
                    sum(
                        [t.last_keypress - t.first_keypress for t in qs],
                        start=timezone.timedelta(0),
                    ).total_seconds()
                    * 1000
                    / len(qs)
                )
            else:
                values_dict["avg_execution_time_ms"] = None

        # Output csv
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="experiment_{}.csv"'.format(code)

        writer = csv.DictWriter(response, no_et[0].keys())
        writer.writeheader()
        writer.writerows(no_et)
        return response


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
