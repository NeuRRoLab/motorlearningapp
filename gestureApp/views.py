import csv
import json
import random
import string
from datetime import datetime
from urllib import parse
import os

from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Max, Min, Q
from django.db import transaction
from django.forms import inlineformset_factory
from django.forms.models import model_to_dict
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    Http404,
    FileResponse,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware, now
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView

from dateutil.tz import tzoffset

from google.cloud import storage
import numpy as np

from .forms import ExperimentCode, UserRegisterForm, BlockFormSet, ExperimentForm
from .models import Block, Experiment, Keypress, Subject, Trial, User, EndSurvey

BUCKET_NAME = "motor-learning"


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

    def form_valid(self, form):
        valid = super(SignUpView, self).form_valid(form)
        username, password = (
            form.cleaned_data.get("username"),
            form.cleaned_data.get("password"),
        )
        # new_user = authenticate(username=username, password=password)
        login(self.request, self.object)
        return valid


class ExperimentCreate(CreateView):
    model = Experiment
    template_name = "gestureApp/experiment_form.html"
    form_class = ExperimentForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ExperimentCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["blocks"] = BlockFormSet(self.request.POST)
        else:
            data["blocks"] = BlockFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        blocks = context["blocks"]
        with transaction.atomic():
            print(form.instance)
        return super(ExperimentCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "gestureApp:experiment_create", kwargs={"pk": self.object.pk}
        )


class ExperimentUpdate(UpdateView):
    model = Experiment
    template_name = "gestureApp/experiment_form.html"
    form_class = ExperimentForm
    success_url = None

    def get_context_data(self, **kwargs):
        data = super(ExperimentUpdate, self).get_context_data(**kwargs)
        if self.request.POST:
            data["blocks"] = BlockFormSet(self.request.POST)
        else:
            data["blocks"] = BlockFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        blocks = context["blocks"]
        with transaction.atomic():
            print(form.instance)
        return super(ExperimentCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "gestureApp:experiment_create", kwargs={"pk": self.object.pk}
        )


def preparation_screen(request):
    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code)
        if not experiment.published or not experiment.enabled:
            raise Http404
        return render(request, "gestureApp/prep_screen.html", {"exp_code": code},)
    else:
        form = ExperimentCode()
        return render(
            request,
            "gestureApp/home.html",
            {"form": form, "error_message": "Form invalid"},
        )


@login_required
def test_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)
    return render(
        request,
        "gestureApp/experiment.html",
        {
            "experiment": experiment.to_dict(),
            "blocks": list(experiment.blocks.order_by("id").values()),
            "test_run": True,
        },
    )


# Create your views here.
def experiment(request):
    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code)
        if not experiment.published or not experiment.enabled:
            raise Http404
        return render(
            request,
            "gestureApp/experiment.html",
            {
                "experiment": experiment.to_dict(),
                "blocks": list(experiment.blocks.order_by("id").values()),
                "test_run": False,
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
    experiment = get_object_or_404(Experiment, pk=exp_code)

    # Create a new subject
    subject = Subject()
    subject.save()
    # Save the trials to database.
    experiment_trials = json.loads(data.get("experiment_trials"))
    tz_offset = data.get("timezone_offset_sec")
    user_timezone = tzoffset(None, tz_offset)
    # print(experiment_trials)
    for i, block in enumerate(experiment_trials):
        for trial in block:
            t = Trial(
                block=experiment.blocks.order_by("id")[i],
                subject=subject,
                started_at=datetime.fromtimestamp(
                    trial["started_at"] / 1000, user_timezone,
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
                    timestamp=datetime.fromtimestamp(timestamp / 1000, user_timezone),
                )
                keypress.save()

    # Create response
    data = {"subject_code": subject.code}
    return JsonResponse(data)


def upload_files(request, pk):
    if request.method == "POST":
        cs_bucket = storage.Client().bucket(BUCKET_NAME)
        handle_upload_file(
            cs_bucket, request.FILES["consent"], pk, "consent.pdf", "application/pdf"
        )
        handle_upload_file(
            cs_bucket,
            request.FILES["video"],
            pk,
            f"video.{str(request.FILES['video']).split('.')[1]}",
            "video/mp4",
        )
        return HttpResponse("Successful")


def handle_upload_file(cs_bucket, file, code, filename, content_type):
    # Upload file to cloud storage
    blob = cs_bucket.blob(f"experiment_files/{code}/{filename}")
    blob.upload_from_string(file.read(), content_type=content_type)
    # if not os.path.exists(f"exp_files/{code}/"):
    #     os.makedirs(f"exp_files/{code}/")
    # # Remove existing file before
    # for f in os.listdir(f"exp_files/{code}/"):
    #     if f.startswith(filename.split(".")[0]):
    #         os.remove(os.path.join(f"exp_files/{code}/", f))

    # with open(f"exp_files/{code}/{filename}", "wb+") as destination:
    #     for chunk in file.chunks():
    #         destination.write(chunk)


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
            with_feedback=exp_info["with_feedback"],
            with_feedback_blocks=exp_info["with_feedback_blocks"],
        )
        for block in exp_info["blocks"]:
            sequence = block["sequence"]
            if block["is_random_sequence"]:
                sequence = "".join(random.choices(string.digits, k=block["seq_length"]))
            # Repeat the block n number of times
            num_repetitions = block["num_repetitions"]
            for _ in range(num_repetitions):
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

        return JsonResponse({"code": experiment.code})

    return render(request, "gestureApp/experiment_form.html", {},)


@login_required
def edit_experiment(request, pk):
    if request.method == "GET":
        experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
        return render(
            request,
            "gestureApp/experiment_form.html",
            {
                "experiment": experiment.to_dict(),
                "blocks": list(experiment.blocks.order_by("id").values()),
            },
        )
    elif request.method == "POST":
        exp_info = json.loads(request.body)
        exp_practice_seq = exp_info["practice_seq"]
        if exp_info["with_practice_trials"] and exp_info["practice_is_random_seq"]:
            exp_practice_seq = "".join(
                random.choices(string.digits, k=exp_info["practice_seq_length"])
            )
        experiment = Experiment.objects.get(pk=exp_info["code"])
        Experiment.objects.filter(pk=exp_info["code"]).update(
            name=exp_info["name"],
            creator=request.user,
            with_practice_trials=exp_info["with_practice_trials"],
            num_practice_trials=exp_info["practice_trials"],
            practice_is_random_seq=exp_info["practice_is_random_seq"],
            practice_seq=exp_practice_seq,
            practice_seq_length=len(exp_practice_seq),
            practice_trial_time=exp_info["practice_trial_time"],
            practice_rest_time=exp_info["practice_rest_time"],
            with_feedback=exp_info["with_feedback"],
            with_feedback_blocks=exp_info["with_feedback_blocks"],
        )
        # Delete blocks not in exp info blocks but that were originally on the experiment
        edit_blocks = [
            block_dict["block_id"]
            for block_dict in exp_info["blocks"]
            if block_dict["block_id"] is not None
        ]
        for block in experiment.blocks.all():
            # if block not in exp_info["blocks"], delete
            if block.id not in edit_blocks:
                block.delete()
        for block in exp_info["blocks"]:
            sequence = block["sequence"]
            if block["is_random_sequence"]:
                sequence = "".join(random.choices(string.digits, k=block["seq_length"]))
            num_repetitions = block["num_repetitions"]
            if block["block_id"] is None:
                for _ in range(num_repetitions):
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
            else:
                block_obj = Block.objects.get(pk=block["block_id"])
                Block.objects.filter(pk=block["block_id"]).update(
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
                if num_repetitions > 1:
                    # Duplicate block as many times as necessary
                    for _ in range(num_repetitions - 1):
                        block_obj.pk = None
                        block_obj.save()
        return HttpResponseRedirect(reverse("gestureApp:profile"))


@login_required
def download_raw_data(request):
    from djqscsv import render_to_csv_response

    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code, creator=request.user)
        # If the experiment hasn't been published, get all responses
        starting_date_useful_data = experiment.created_at
        # If it has, then only get those after the publishing timestamp
        if experiment.published:
            starting_date_useful_data = experiment.published_timestamp
        # Make sure that the user downloading it is the owner of the experiment
        qs = Experiment.objects.filter(
            pk=code,
            creator=request.user,
            blocks__trials__started_at__gt=starting_date_useful_data,
        ).values(
            experiment_code=F("code"),
            subject_code=F("blocks__trials__subject__code"),
            block_id=F("blocks"),
            block_sequence=F("blocks__sequence"),
            trial_id=F("blocks__trials__id"),
            correct_input=F("blocks__trials__correct"),
            keypress_timestamp=F("blocks__trials__keypresses__timestamp"),
            keypress_value=F("blocks__trials__keypresses__value"),
        )
        queryset_list = list(qs)
        # Order subjects by time when they started the first trial
        subjects = [
            Subject.objects.get(pk=code)
            for code in unique([value["subject_code"] for value in queryset_list])
        ]
        subjects.sort(
            key=lambda subj: subj.trials.order_by("started_at").first().started_at
        )
        possible_subjects = [subj.code for subj in subjects]
        new_subject_codes = {
            subject: index + 1 for index, subject in enumerate(possible_subjects)
        }
        new_subject_codes = {
            subject: index + 1 for index, subject in enumerate(possible_subjects)
        }
        # FIXME: may be necessary to force the ordering of trials and blocks
        possible_blocks = unique([value["block_id"] for value in queryset_list])
        new_block_codes = {
            block: index + 1 for index, block in enumerate(possible_blocks)
        }
        # Trials are not fixed across different experiments or blocks.
        # If we are on the same experiment and block, start adding up
        # for every combination of block-subject, we have a different count
        # {(block, subject): [trial_1, trial_2, trial_3]}
        aux_values = defaultdict(dict)
        for values_dict in queryset_list:
            trial_id_dict = aux_values[
                (values_dict["block_id"], values_dict["subject_code"])
            ]
            if values_dict["trial_id"] not in trial_id_dict:
                trial_id_dict[values_dict["trial_id"]] = len(trial_id_dict.keys()) + 1
        # Change the subject, block and trials ids to a numbered code
        for values_dict in queryset_list:
            values_dict["trial_id"] = aux_values[
                (values_dict["block_id"], values_dict["subject_code"])
            ][values_dict["trial_id"]]
            values_dict["subject_code"] = new_subject_codes[values_dict["subject_code"]]
            values_dict["block_id"] = new_block_codes[values_dict["block_id"]]
            # values_dict["trial_id"] = new_trial_codes[values_dict["trial_id"]]
        # Order the list by block and then subject
        queryset_list.sort(
            key=lambda value_dict: (
                value_dict["subject_code"],
                value_dict["block_id"],
                value_dict["trial_id"],
                value_dict["keypress_timestamp"],
            )
        )
        keypresses = [
            (v_dict["keypress_timestamp"], v_dict["subject_code"])
            for v_dict in queryset_list
        ]
        diff_keypresses_ms = [None] + [
            (y[0] - x[0]).total_seconds() * 1000
            if x[1] == y[1] and x[0] is not None and y[0] is not None
            else None
            for x, y in zip(keypresses, keypresses[1:])
        ]
        for values_dict, diff in zip(queryset_list, diff_keypresses_ms):
            if values_dict["keypress_timestamp"] is not None:
                values_dict["keypress_timestamp"] = values_dict[
                    "keypress_timestamp"
                ].strftime("%Y-%m-%d %H:%M:%S.%f")
            values_dict["diff_between_keypresses_ms"] = diff

        # Output csv
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="raw_experiment_{}.csv"'.format(code)

        writer = csv.DictWriter(response, queryset_list[0].keys())
        writer.writeheader()
        writer.writerows(queryset_list)
        return response


@login_required
def download_processed_data(request):
    from djqscsv import render_to_csv_response

    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data["code"]
        experiment = get_object_or_404(Experiment, pk=code, creator=request.user)
        # If the experiment hasn't been published, get all responses
        starting_date_useful_data = experiment.created_at
        # If it has, then only get those after the publishing timestamp
        if experiment.published:
            starting_date_useful_data = experiment.published_timestamp
        # Make sure that the user downloading it is the owner of the experiment
        # When not working with sqlite, we will be able to do something like this:
        #   Trial.objects.filter(block__experiment__code="952P", block=12,subject="E7kMfKZHIZjL375d",correct=True).annotate(first_keypress=Min("keypresses__timestamp")).annotate(last_keypress=Max("keypresses__timestamp")).aggregate(avg_diff=Avg(F("first_keypress")-F("last_keypress")))
        no_et = (
            Experiment.objects.filter(
                pk=code,
                creator=request.user,
                blocks__trials__started_at__gt=starting_date_useful_data,
            )
            .values(
                "code",
                "blocks",
                "blocks__trials__subject",
                "blocks__sequence",
                "blocks__trials",
                "blocks__trials__correct",
            )
            .distinct()
            # .annotate(
            #     num_correct_trials=Count(
            #         "blocks__trials", filter=Q(blocks__trials__correct=True)
            #     )
            # )
            # .annotate(total_trials=Count("blocks__trials"))
        )
        no_et = list(no_et)
        acc_correct_trials = defaultdict(lambda: 0)
        for values_dict in no_et:
            values_dict["experiment_code"] = values_dict.pop("code")
            values_dict["subject_code"] = values_dict.pop("blocks__trials__subject")
            values_dict["block_id"] = values_dict.pop("blocks")
            values_dict["block_sequence"] = values_dict.pop("blocks__sequence")
            values_dict["trial_id"] = values_dict.pop("blocks__trials")
            values_dict["correct_trial"] = values_dict.pop("blocks__trials__correct")
            if values_dict["correct_trial"]:
                acc_correct_trials[
                    (values_dict["block_id"], values_dict["subject_code"])
                ] += 1
            values_dict["accumulated_correct_trials"] = acc_correct_trials[
                (values_dict["block_id"], values_dict["subject_code"])
            ]
            # values_dict["num_correct_trials"] = values_dict.pop("num_correct_trials")
            # values_dict["total_trials"] = values_dict.pop("total_trials")
        accumulated_keypresses = defaultdict(lambda: 0)
        accumulated_elapsed_time = defaultdict(lambda: 0)
        for values_dict in no_et:
            # TODO: if the difference between the starting timestamp of trial and last keypress is desired, change
            qs = (
                Trial.objects.filter(pk=values_dict["trial_id"], correct=True)
                .annotate(first_keypress=Min("keypresses__timestamp"))
                .annotate(last_keypress=Max("keypresses__timestamp"))
            )
            if len(qs) > 0:
                # Tapping speed
                tap_speed = []
                keypresses = qs[0].keypresses.order_by("timestamp")
                for index, keypress in enumerate(keypresses):
                    if index == 0:
                        continue
                    elapsed = (
                        keypress.timestamp - keypresses[index - 1].timestamp
                    ).total_seconds()
                    tap_speed.append(1.0 / elapsed)
                # Mean and std deviation of tapping speed
                mean_tap_speed = np.mean(tap_speed)
                std_dev_tap_speed = np.std(tap_speed, ddof=1)

                # Execution time
                execution_time_ms = (
                    qs[0].last_keypress - qs[0].first_keypress
                ).total_seconds() * 1000
                values_dict["execution_time_ms"] = execution_time_ms
                # Tapping data
                values_dict["tapping_speed_mean"] = mean_tap_speed
                values_dict["tapping_speed_std_dev"] = std_dev_tap_speed

                # Accumulated tapping data
                # accumulated_keypresses[
                #     (values_dict["block_id"], values_dict["subject_code"])
                # ] += len(qs[0].block.sequence)
                # accumulated_elapsed_time[
                #     (values_dict["block_id"], values_dict["subject_code"])
                # ] += (execution_time_ms / 1000.0)

            else:
                values_dict["execution_time_ms"] = None
                # Tapping data
                values_dict["tapping_speed_mean"] = None
                values_dict["tapping_speed_std_dev"] = None

            # if (
            #     accumulated_elapsed_time[
            #         values_dict["block_id"], values_dict["subject_code"]
            #     ]
            #     != 0
            # ):
            #     values_dict["accumulated_tapping_speed"] = (
            #         accumulated_keypresses[
            #             (values_dict["block_id"], values_dict["subject_code"])
            #         ]
            #         / accumulated_elapsed_time[
            #             (values_dict["block_id"], values_dict["subject_code"])
            #         ]
            #     )
            # else:
            #     values_dict["accumulated_tapping_speed"] = 0
        # Order subjects by time when they started the first trial
        subjects = [
            Subject.objects.get(pk=code)
            for code in unique([value["subject_code"] for value in no_et])
        ]
        # Sort by time when the user started the first trial
        subjects.sort(
            key=lambda subj: subj.trials.order_by("started_at").first().started_at
        )
        possible_subjects = [subj.code for subj in subjects]
        new_subject_codes = {
            subject: index + 1 for index, subject in enumerate(possible_subjects)
        }
        possible_blocks = unique([value["block_id"] for value in no_et])
        new_block_codes = {
            block: index + 1 for index, block in enumerate(possible_blocks)
        }
        # Trials are not fixed across different experiments or blocks.
        # If we are on the same experiment and block, start adding up
        # for every combination of block-subject, we have a different count
        # {(block, subject): {trial_1: 1, trial_2:2, trial_3:3}}
        aux_values = defaultdict(dict)
        for values_dict in no_et:
            # To get the new id
            trial_id_dict = aux_values[
                (values_dict["block_id"], values_dict["subject_code"])
            ]
            if values_dict["trial_id"] not in trial_id_dict:
                trial_id_dict[values_dict["trial_id"]] = len(trial_id_dict.keys()) + 1
        # Change the subject, block and trials ids to a numbered code
        for values_dict in no_et:
            values_dict["trial_id"] = aux_values[
                (values_dict["block_id"], values_dict["subject_code"])
            ][values_dict["trial_id"]]
            values_dict["subject_code"] = new_subject_codes[values_dict["subject_code"]]
            values_dict["block_id"] = new_block_codes[values_dict["block_id"]]
            # values_dict["trial_id"] = new_trial_codes[values_dict["trial_id"]]
        # Order the list by block and then subject
        no_et.sort(
            key=lambda value_dict: (
                value_dict["subject_code"],
                value_dict["block_id"],
                value_dict["trial_id"],
            )
        )
        # Output csv
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="processed_experiment_{}.csv"'.format(code)

        writer = csv.DictWriter(response, no_et[0].keys())
        writer.writeheader()
        writer.writerows(no_et)
        return response


@login_required
def download_survey(request, pk):
    # Get all experiments subjects
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    # If the experiment hasn't been published, get all responses
    starting_date_useful_data = experiment.created_at
    # If it has, then only get those after the publishing timestamp
    if experiment.published:
        starting_date_useful_data = experiment.published_timestamp
    # For each subject, check if it has a survey
    subjects_surveys = (
        Experiment.objects.filter(
            pk=pk,
            creator=request.user,
            blocks__trials__started_at__gt=starting_date_useful_data,
        )
        .values("code", "blocks__trials__subject", "blocks__trials__subject__survey")
        .distinct()
    )
    subjects_surveys = list(subjects_surveys)
    # Order subjects by time when they started the first trial
    subjects = [
        Subject.objects.get(pk=code)
        for code in unique(
            [value["blocks__trials__subject"] for value in subjects_surveys]
        )
    ]
    # Sort by time when the user started the first trial
    subjects.sort(
        key=lambda subj: subj.trials.order_by("started_at").first().started_at
    )
    possible_subjects = [
        (subj.code, subj.trials.order_by("started_at").first()) for subj in subjects
    ]
    new_subject_codes = {
        subject: (index + 1, timestamp)
        for index, (subject, timestamp) in enumerate(possible_subjects)
    }
    # If they do, complete the row. If not, keep it empty.
    survey = {
        "age": "Age",
        "gender": "Gender",
        "comp_type": "Computer Type",
        "comments": "Comments",
    }
    for values_dict in subjects_surveys:
        values_dict["experiment_code"] = values_dict.pop("code")
        started_experiment_at = values_dict[
            "started_experiment_at"
        ] = new_subject_codes[values_dict["blocks__trials__subject"]][1]
        values_dict["subject_code"] = new_subject_codes[
            values_dict.pop("blocks__trials__subject")
        ][0]
        values_dict["started_experiment_at"] = started_experiment_at

        for value in survey.values():
            values_dict[value] = None
        if values_dict["blocks__trials__subject__survey"] is not None:
            # Add survey values
            survey_id = values_dict["blocks__trials__subject__survey"]
            survey_obj = EndSurvey.objects.get(pk=survey_id)
            for key, value in survey.items():
                values_dict[value] = getattr(survey_obj, key)
        values_dict.pop("blocks__trials__subject__survey")
    # Order the list by block and then subject
    subjects_surveys.sort(key=lambda value_dict: (value_dict["subject_code"]))
    # Output csv
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="survey_experiment_{}.csv"'.format(pk)

    writer = csv.DictWriter(response, subjects_surveys[0].keys())
    writer.writeheader()
    writer.writerows(subjects_surveys)
    return response


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


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
            exp_obj["published"] = experiment.published
            if experiment.published:
                exp_obj["responses"] = (
                    Subject.objects.filter(
                        trials__block__experiment=experiment,
                        trials__started_at__gt=experiment.published_timestamp,
                    )
                    .distinct()
                    .count()
                )
            else:
                exp_obj["responses"] = (
                    Subject.objects.filter(trials__block__experiment=experiment)
                    .distinct()
                    .count()
                )
            exp_obj["enabled"] = experiment.enabled
            exp_array.append(exp_obj)
        return JsonResponse({"experiments": exp_array})


@login_required
def publish_experiment(request, pk):
    # Get experiment from code
    # Change the published status to true, and add the published timestamp
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    if experiment.published:
        return JsonResponse({})
    experiment.published = True
    experiment.published_timestamp = timezone.now()
    experiment.save()
    return JsonResponse({})


@login_required
def delete_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    experiment.delete()
    return JsonResponse({})


@login_required
def disable_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    experiment.enabled = False
    experiment.save()
    return JsonResponse({})


@login_required
def enable_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    experiment.enabled = True
    experiment.save()
    return JsonResponse({})


@login_required
def duplicate_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    experiment_clone = experiment.make_clone(
        attrs={"name": "Copy of " + experiment.name}
    )
    return JsonResponse({})


def end_survey(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)
    info = json.loads(request.body)
    subject = None
    try:
        subject = Subject.objects.get(code=info["subject_code"])
    except Subject.DoesNotExist:
        pass
    survey = EndSurvey.objects.create(
        experiment=experiment,
        subject=subject,
        age=info["questionnaire"]["age"],
        gender=info["questionnaire"]["gender"],
        comments=info["questionnaire"]["comment"],
        comp_type=info["questionnaire"]["comp_type"],
    )
    return JsonResponse({})
