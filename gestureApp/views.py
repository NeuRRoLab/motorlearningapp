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
from django.core.mail import send_mail
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
from django.shortcuts import get_object_or_404, redirect, render
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
from .models import Block, Experiment, Keypress, Subject, Trial, User, EndSurvey, Study

BUCKET_NAME = "motor-learning"


@method_decorator([login_required], name="dispatch")
class Profile(DetailView):
    model = User
    template_name = "gestureApp/profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["experiments"] = self.request.user.experiments.all().order_by(
            "created_at"
        )
        context["studies"] = self.request.user.studies.all().order_by("created_at")
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


# def preparation_screen(request):
#     form = ExperimentCode(request.GET)
#     if form.is_valid():
#         code = form.cleaned_data["code"]
#         experiment = get_object_or_404(Experiment, pk=code)
#         if not experiment.published or not experiment.enabled:
#             raise Http404
#         return render(request, "gestureApp/prep_screen.html", {"exp_code": code},)
#     else:
#         form = ExperimentCode()
#         return render(
#             request,
#             "gestureApp/home.html",
#             {"form": form, "error_message": "Form invalid"},
#         )


def study(request, pk):
    # Get subject code
    subject_code = request.GET.get("subj-code", None)
    study = get_object_or_404(Study, pk=pk, published=True, enabled=True)
    # Exclude disabled experiments
    experiment = study.experiments.filter(enabled=True).order_by("?").first()
    if experiment is None:
        # No enabled experiments in this study
        return Http404

    # Do the randomization here and redirect to the appropiate experiment
    return redirect(f"/experiment/{experiment.code}/?subj_code={subject_code}")


# Create your views here.
def experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)
    subject_code = request.GET.get("subj-code", None)
    if subject_code is not None and subject_code != "":
        subject = get_object_or_404(Subject, pk=subject_code)
        # Check if that subject already participated in this experiment
        if experiment.blocks.filter(trials__subject=subject).exists():
            raise Exception("Subject already participated in experiment")
    if not experiment.published or not experiment.enabled:
        # If not testing experiment, raise 404
        print(request.user)
        if experiment.creator != request.user:
            raise Http404
    return render(
        request,
        "gestureApp/experiment.html",
        {
            "experiment": experiment.to_dict(),
            "blocks": list(experiment.blocks.order_by("id").values()),
            "subject_code": subject_code,
        },
    )


def home(request):
    form = ExperimentCode()
    return render(request, "gestureApp/home.html", {"form": form})


def create_trials(request):
    data = json.loads(request.body)
    exp_code = data.get("experiment")
    experiment = get_object_or_404(Experiment, pk=exp_code)
    subj_code = data.get("subject_code")

    # Create a new subject
    subject = None
    if subj_code is not None and subj_code != "":
        subject = get_object_or_404(Subject, pk=subj_code)
    else:
        subject = Subject.objects.create()
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
                partial_correct=trial["partial_correct"],
                finished_at=datetime.fromtimestamp(
                    trial["finished_at"] / 1000, user_timezone,
                ),
            )
            t.save()
            for keypress in trial["keypresses"]:
                value = keypress["value"]
                # Don't count special characters
                if len(value) > 1:
                    continue
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
        study = get_object_or_404(Study, pk=exp_info["study"])
        exp_practice_seq = exp_info["practice_seq"]
        if exp_info["with_practice_trials"] and exp_info["practice_is_random_seq"]:
            exp_practice_seq = "".join(
                random.choices(string.digits, k=exp_info["practice_seq_length"])
            )
        experiment = Experiment.objects.create(
            name=exp_info["name"],
            study=study,
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
            rest_after_practice=exp_info["rest_after_practice"],
            requirements=exp_info["requirements"],
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
            rest_after_practice=exp_info["rest_after_practice"],
            requirements=exp_info["requirements"],
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
def create_study(request):
    if request.method == "POST":
        study_info = json.loads(request.body)
        study = Study.objects.create(
            name=study_info["name"],
            creator=request.user,
            description=study_info["description"],
        )

        return JsonResponse({"code": study.code})

    return render(request, "gestureApp/study_form.html", {},)


@login_required
def edit_study(request, pk):
    if request.method == "GET":
        study = get_object_or_404(Study, pk=pk, creator=request.user)
        return render(
            request, "gestureApp/study_form.html", {"study": study.to_dict(),},
        )
    elif request.method == "POST":
        study_info = json.loads(request.body)
        study = Study.objects.get(pk=study_info["code"])
        Study.objects.filter(pk=study_info["code"]).update(
            name=study_info["name"],
            creator=request.user,
            description=study_info["description"],
        )
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
        qs = (
            Experiment.objects.filter(
                pk=code,
                creator=request.user,
                blocks__trials__started_at__gt=starting_date_useful_data,
            )
            .order_by("blocks__trials__keypresses__timestamp")
            .values(
                experiment_code=F("code"),
                subject_code=F("blocks__trials__subject__code"),
                block_id=F("blocks"),
                block_sequence=F("blocks__sequence"),
                trial_id=F("blocks__trials__id"),
                was_trial_correct=F("blocks__trials__correct"),
                was_partial_trial_correct=F("blocks__trials__partial_correct"),
                keypress_timestamp=F("blocks__trials__keypresses__timestamp"),
                keypress_value=F("blocks__trials__keypresses__value"),
            )
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
        subjects_starting_timestamp = {
            subject.code: subject.trials.order_by("started_at").first().started_at
            for subject in subjects
        }
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
            # values_dict["subject_code"] = new_subject_codes[values_dict["subject_code"]]
            values_dict["block_id"] = new_block_codes[values_dict["block_id"]]
            # values_dict["trial_id"] = new_trial_codes[values_dict["trial_id"]]
        # Order the list by block and then subject
        queryset_list.sort(
            key=lambda value_dict: (
                subjects_starting_timestamp[value_dict["subject_code"]],
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
        # Calculate whether or not the keypress input was correct
        # We'll get all keypresses for each trial, and then compare them with the trial sequence
        current_trial = -1
        current_block = -1
        current_subject = ""
        current_trial_seq_idx = 0
        for values_dict, diff in zip(queryset_list, diff_keypresses_ms):
            print(values_dict)
            # Was keypress correct
            if (
                current_trial == values_dict["trial_id"]
                and current_block == values_dict["block_id"]
                and current_subject == values_dict["subject_code"]
            ):
                # When on the same trial and block, increase the sequence index
                current_trial_seq_idx += 1
            else:
                # When on a different trial or block, restart the counters
                current_trial = values_dict["trial_id"]
                current_block = values_dict["block_id"]
                current_subject = values_dict["subject_code"]
                current_trial_seq_idx = 0
            if (
                values_dict["block_sequence"][current_trial_seq_idx]
                == values_dict["keypress_value"]
            ):
                # If the corresponding value of the sequence is equal to the keypress, show True, else False
                values_dict["was_keypress_correct"] = True
            else:
                values_dict["was_keypress_correct"] = False
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

        if len(queryset_list) > 0:
            writer = csv.DictWriter(response, queryset_list[0].keys())
            writer.writeheader()
        else:
            writer = csv.DictWriter(response, ["experiment"])
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
        )
        no_et = list(no_et)
        acc_correct_trials = defaultdict(lambda: 0)
        # acc_partial_correct_trials = defaultdict(lambda: 0)
        for values_dict in no_et:
            values_dict["experiment_code"] = values_dict.pop("code")
            values_dict["subject_code"] = values_dict.pop("blocks__trials__subject")
            values_dict["block_id"] = values_dict.pop("blocks")
            values_dict["block_sequence"] = values_dict.pop("blocks__sequence")
            values_dict["trial_id"] = values_dict.pop("blocks__trials")
            values_dict["correct_trial"] = values_dict.pop("blocks__trials__correct")
            # values_dict["correct_partial_trial"] = values_dict.pop(
            #     "blocks__trials__partial_correct"
            # )
            if values_dict["correct_trial"]:
                acc_correct_trials[
                    (values_dict["block_id"], values_dict["subject_code"])
                ] += 1
            # if values_dict["correct_partial_trial"]:
            #     acc_partial_correct_trials[
            #         (values_dict["block_id"], values_dict["subject_code"])
            #     ] += 1
            values_dict["accumulated_correct_trials"] = acc_correct_trials[
                (values_dict["block_id"], values_dict["subject_code"])
            ]
            # values_dict[
            #     "accumulated_partial_correct_trials"
            # ] = acc_partial_correct_trials[
            #     (values_dict["block_id"], values_dict["subject_code"])
            # ]
            # values_dict["num_correct_trials"] = values_dict.pop("num_correct_trials")
            # values_dict["total_trials"] = values_dict.pop("total_trials")
        accumulated_keypresses = defaultdict(lambda: 0)
        accumulated_elapsed_time = defaultdict(lambda: 0)
        for idx, values_dict in enumerate(no_et):
            # TODO: if the difference between the starting timestamp of trial and last keypress is desired, change
            qs = (
                Trial.objects.filter(correct=True, pk=values_dict["trial_id"])
                .annotate(first_keypress=Min("keypresses__timestamp"))
                .annotate(last_keypress=Max("keypresses__timestamp"))
            )
            # Next trial: closest starting timestamp in the same block and subject
            skip_trial = False
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
                    if elapsed == 0:
                        # Something failed while capturing the keypresses timestamp. we should skip this trial.
                        # We could say that the elapsed value is the minimum possible keypress difference (1ms)
                        # This keypress would get discarded anyway.
                        elapsed = 0.001
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
                values_dict["tapping_speed_mean"] = (
                    mean_tap_speed if not np.isnan(mean_tap_speed) else None
                )
                values_dict["tapping_speed_std_dev"] = (
                    std_dev_tap_speed if not np.isnan(std_dev_tap_speed) else None
                )

                # Cohen metrics: time between first keypress of this trial, and first keypress of the next
                # execution_time_ms = (
                #     qs[0].last_keypress - qs[0].first_keypress
                # ).total_seconds() * 1000

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
        subjects_starting_timestamp = {
            subject.code: subject.trials.order_by("started_at").first().started_at
            for subject in subjects
        }
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
            # values_dict["subject_code"] = new_subject_codes[values_dict["subject_code"]]
            values_dict["block_id"] = new_block_codes[values_dict["block_id"]]
            # values_dict["trial_id"] = new_trial_codes[values_dict["trial_id"]]
        # Order the list by block and then subject
        no_et.sort(
            key=lambda value_dict: (
                subjects_starting_timestamp[value_dict["subject_code"]],
                value_dict["block_id"],
                value_dict["trial_id"],
            )
        )
        # Output csv
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="processed_experiment_{}.csv"'.format(code)
        if len(no_et) > 0:
            writer = csv.DictWriter(response, no_et[0].keys())
            writer.writeheader()
        else:
            writer = csv.DictWriter(response, ["experiment"])
        writer.writerows(no_et)
        return response


# FIXME: this is failing
# /home/lhcubillos/.local/lib/python3.8/site-packages/numpy/core/_methods.py:233: RuntimeWarning: Degrees of freedom <= 0 for slice
#   ret = _var(a, axis=axis, dtype=dtype, out=out, ddof=ddof,
# /home/lhcubillos/.local/lib/python3.8/site-packages/numpy/core/_methods.py:226: RuntimeWarning: invalid value encountered in double_scalars
#   ret = ret.dtype.type(ret / rcount)
# /home/lhcubillos/.local/lib/python3.8/site-packages/numpy/core/fromnumeric.py:3372: RuntimeWarning: Mean of empty slice.
#   return _methods._mean(a, axis=axis, dtype=dtype,
# /home/lhcubillos/.local/lib/python3.8/site-packages/numpy/core/_methods.py:170: RuntimeWarning: invalid value encountered in double_scalars
#   ret = ret.dtype.type(ret / rcount)
# /home/lhcubillos/.local/lib/python3.8/site-packages/numpy/core/_methods.py:194: RuntimeWarning: invalid value encountered in true_divide
#   arrmean = um.true_divide(


@login_required
def download_cohen_processed(request, pk):
    # Get all experiments subjects
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    # If the experiment hasn't been published, get all responses
    starting_date_useful_data = experiment.created_at
    # If it has, then only get those after the publishing timestamp
    if experiment.published:
        starting_date_useful_data = experiment.published_timestamp

    results = (
        Experiment.objects.filter(
            pk=pk,
            creator=request.user,
            blocks__trials__started_at__gt=starting_date_useful_data,
        )
        .values(
            "code",
            "blocks",
            "blocks__trials__subject",
            "blocks__sequence",
            "blocks__trials",
            "blocks__trials__partial_correct",
        )
        .distinct()
    )
    results = list(results)

    acc_correct_trials = defaultdict(lambda: 0)
    for values_dict in results:
        values_dict["experiment_code"] = values_dict.pop("code")
        values_dict["subject_code"] = values_dict.pop("blocks__trials__subject")
        values_dict["block_id"] = values_dict.pop("blocks")
        values_dict["block_sequence"] = values_dict.pop("blocks__sequence")
        values_dict["trial_id"] = values_dict.pop("blocks__trials")
        values_dict["correct_trial"] = values_dict.pop(
            "blocks__trials__partial_correct"
        )
        if values_dict["correct_trial"]:
            acc_correct_trials[
                (values_dict["block_id"], values_dict["subject_code"])
            ] += 1
        values_dict["accumulated_correct_trials"] = acc_correct_trials[
            (values_dict["block_id"], values_dict["subject_code"])
        ]

    # For each block, subject, get the first and last trial starting and finish timestamps.
    trial_timestamps = {}
    block_results = (
        Block.objects.filter(experiment__code=pk, trials__partial_correct=True)
        .annotate(first_trial_started_at=Min("trials__started_at"))
        .annotate(last_trial_finished_at=Max("trials__finished_at"))
        .values(
            "id", "trials__subject", "first_trial_started_at", "last_trial_finished_at"
        )
    )
    for values_dict in block_results:
        trial_timestamps[(values_dict["id"], values_dict["trials__subject"])] = (
            values_dict["first_trial_started_at"],
            values_dict["last_trial_finished_at"],
        )

    for values_dict in results:
        # If first trial of block: difference between starting of trial and first keypress of next.
        # If last trial of block: difference between first keypress and end of trial
        # else: difference between first keypress of this block, and first of the next.
        qs = Trial.objects.filter(
            Q(correct=True) | Q(partial_correct=True), pk=values_dict["trial_id"],
        ).annotate(first_keypress=Min("keypresses__timestamp"))
        # Next trial: closest starting timestamp in the same block and subject
        if len(qs) > 0:
            trial = qs[0]
            execution_time_ms = -1
            # Check if the trial is the last one of the block
            if (
                trial.finished_at
                == trial_timestamps[
                    (values_dict["block_id"], values_dict["subject_code"])
                ][1]
            ):
                execution_time_ms = (
                    trial.finished_at - trial.first_keypress
                ).total_seconds() * 1000
            # Else, get next trial: same subject and block, minimum starting time that is greater than this finishing time
            else:
                next_trial = (
                    Trial.objects.filter(
                        subject=trial.subject,
                        block=trial.block,
                        started_at__gte=trial.finished_at,
                    )
                    .order_by("started_at")
                    .annotate(first_keypress=Min("keypresses__timestamp"))[0]
                )
                # Check if it's the first trial
                if (
                    trial.started_at
                    == trial_timestamps[
                        (values_dict["block_id"], values_dict["subject_code"])
                    ][0]
                ):
                    execution_time_ms = (
                        next_trial.first_keypress - trial.started_at
                    ).total_seconds() * 1000
                else:
                    execution_time_ms = (
                        next_trial.first_keypress - trial.first_keypress
                    ).total_seconds() * 1000
            # Tapping speed
            tap_speed = []
            keypresses = trial.keypresses.order_by("timestamp")
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
            # execution_time_ms = (
            #     trial.last_keypress - trial.first_keypress
            # ).total_seconds() * 1000
            values_dict["execution_time_ms"] = execution_time_ms
            # Tapping data
            values_dict["tapping_speed_mean"] = (
                mean_tap_speed if not np.isnan(mean_tap_speed) else None
            )
            values_dict["tapping_speed_std_dev"] = (
                std_dev_tap_speed if not np.isnan(std_dev_tap_speed) else None
            )
        else:
            values_dict["execution_time_ms"] = None
            # Tapping data
            values_dict["tapping_speed_mean"] = None
            values_dict["tapping_speed_std_dev"] = None
    # Order subjects by time when they started the first trial
    subjects = [
        Subject.objects.get(pk=code)
        for code in unique([value["subject_code"] for value in results])
    ]
    # Sort by time when the user started the first trial
    subjects.sort(
        key=lambda subj: subj.trials.order_by("started_at").first().started_at
    )
    possible_subjects = [subj.code for subj in subjects]
    new_subject_codes = {
        subject: index + 1 for index, subject in enumerate(possible_subjects)
    }
    possible_blocks = unique([value["block_id"] for value in results])
    new_block_codes = {block: index + 1 for index, block in enumerate(possible_blocks)}
    # Trials are not fixed across different experiments or blocks.
    # If we are on the same experiment and block, start adding up
    # for every combination of block-subject, we have a different count
    # {(block, subject): {trial_1: 1, trial_2:2, trial_3:3}}
    aux_values = defaultdict(dict)
    for values_dict in results:
        # To get the new id
        trial_id_dict = aux_values[
            (values_dict["block_id"], values_dict["subject_code"])
        ]
        if values_dict["trial_id"] not in trial_id_dict:
            trial_id_dict[values_dict["trial_id"]] = len(trial_id_dict.keys()) + 1
    # Change the subject, block and trials ids to a numbered code
    for values_dict in results:
        values_dict["trial_id"] = aux_values[
            (values_dict["block_id"], values_dict["subject_code"])
        ][values_dict["trial_id"]]
        values_dict["subject_code"] = new_subject_codes[values_dict["subject_code"]]
        values_dict["block_id"] = new_block_codes[values_dict["block_id"]]
        # values_dict["trial_id"] = new_trial_codes[values_dict["trial_id"]]
    # Order the list by block and then subject
    results.sort(
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
    ] = 'attachment; filename="cohen_processed_experiment_{}.csv"'.format(pk)
    if len(results) > 0:
        writer = csv.DictWriter(response, results[0].keys())
        writer.writeheader()
    else:
        writer = csv.DictWriter(response, ["experiment"])
    writer.writerows(results)
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
    subjects_starting_timestamp = {
        subject.code: subject.trials.order_by("started_at").first().started_at
        for subject in subjects
    }
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
        "medical_condition": "Medical condition",
        "hours_of_sleep": "Hours of Sleep night before",
        "excercise_regularly": "Excercise Regularly",
        "level_education": "Level of Education",
        "keypress_experiment_before": "Done keypress experiment before",
        "followed_instructions": "Followed instructions",
        "hand_used": "Hand used for experiment",
        "dominant_hand": "Dominant Hand",
        "comments": "Comments",
    }
    for values_dict in subjects_surveys:
        values_dict["experiment_code"] = values_dict.pop("code")
        started_experiment_at = new_subject_codes[
            values_dict["blocks__trials__subject"]
        ][1]
        values_dict["subject_code"] = values_dict.pop("blocks__trials__subject")
        # values_dict["subject_code"] = new_subject_codes[
        #     values_dict.pop("blocks__trials__subject")
        # ][0]
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
    subjects_surveys.sort(
        key=lambda value_dict: (subjects_starting_timestamp[value_dict["subject_code"]])
    )
    # Output csv
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="survey_experiment_{}.csv"'.format(pk)

    if len(subjects_surveys) > 0:
        writer = csv.DictWriter(response, subjects_surveys[0].keys())
        writer.writeheader()
    else:
        writer = csv.DictWriter(response, ["experiment"])
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
def user_studies(request):
    if request.method == "GET":
        study_array = []
        for study in request.user.studies.all():
            study_obj = {}
            study_obj["code"] = study.code
            study_obj["name"] = study.name
            study_obj["published"] = study.published
            study_obj["enabled"] = study.enabled
            study_obj["experiments"] = []
            for experiment in study.experiments.all():
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
                study_obj["experiments"].append(exp_obj)
            study_array.append(study_obj)
        return JsonResponse({"studies": study_array})


def _publish_experiment(experiment):
    # Get experiment from code
    # Change the published status to true, and add the published timestamp
    if experiment.published:
        return
    experiment.published = True
    experiment.published_timestamp = timezone.now()
    experiment.save()
    return


@login_required
def delete_experiment(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk, creator=request.user)
    # Remove stuff from Cloud Storage
    cs_bucket = storage.Client().bucket(BUCKET_NAME)
    blobs = cs_bucket.list_blobs(prefix=f"experiment_files/{pk}")
    for blob in blobs:
        blob.delete()

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
    original_pk_experiment = experiment.pk
    blocks = list(experiment.blocks.order_by("id"))
    # Clone
    experiment.pk = None
    experiment.name = "Copy of " + experiment.name
    experiment.save()

    # Clone blocks
    for block in blocks:
        block.pk = None
        block.experiment = experiment
        block.save()

    # Copy the consent and video
    cs_bucket = storage.Client().bucket(BUCKET_NAME)
    source_consent = cs_bucket.blob(
        f"experiment_files/{original_pk_experiment}/consent.pdf"
    )
    source_video = cs_bucket.blob(
        f"experiment_files/{original_pk_experiment}/video.mp4"
    )

    # Consent
    cs_bucket.copy_blob(
        source_consent, cs_bucket, f"experiment_files/{experiment.pk}/consent.pdf"
    )
    # Video
    cs_bucket.copy_blob(
        source_video, cs_bucket, f"experiment_files/{experiment.pk}/video.mp4"
    )
    return JsonResponse({})


@login_required
def publish_study(request, pk):
    # Get study from code
    # Change the published status to true, and add the published timestamp
    study = get_object_or_404(Study, pk=pk, creator=request.user)
    if study.published:
        return JsonResponse({})
    study.published = True
    study.published_timestamp = timezone.now()
    study.save()
    # Publish all experiments in this study
    for experiment in study.experiments.all():
        _publish_experiment(experiment)
    return JsonResponse({})


@login_required
def delete_study(request, pk):
    study = get_object_or_404(Study, pk=pk, creator=request.user)
    study.delete()
    return JsonResponse({})


@login_required
def disable_study(request, pk):
    study = get_object_or_404(Study, pk=pk, creator=request.user)
    study.enabled = False
    study.save()
    return JsonResponse({})


@login_required
def enable_study(request, pk):
    study = get_object_or_404(Study, pk=pk, creator=request.user)
    study.enabled = True
    study.save()
    return JsonResponse({})


@login_required
def duplicate_study(request, pk):
    study = get_object_or_404(Study, pk=pk, creator=request.user)
    original_pk_study = study.pk
    # Clone
    study.pk = None
    study.name = "Copy of " + study.name
    study.save()
    # TODO: maybe clone the experiments as well
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
        medical_condition=info["questionnaire"]["medical_condition"],
        hours_of_sleep=info["questionnaire"]["hours_of_sleep"],
        excercise_regularly=info["questionnaire"]["excercise_regularly"],
        keypress_experiment_before=info["questionnaire"]["keypress_experiment_before"],
        followed_instructions=info["questionnaire"]["followed_instructions"],
        hand_used=info["questionnaire"]["hand_used"],
        dominant_hand=info["questionnaire"]["dominant_hand"],
        level_education=info["questionnaire"]["level_education"],
    )
    return JsonResponse({})


def create_subject(request):
    subject = Subject.objects.create()
    print(subject)
    return JsonResponse({"subject_code": subject.code})


def send_subject_code(request):
    if request.method == "POST":
        # Get subject code from post data
        data = json.loads(request.body)
        subject_code = data["subject_code"]
        email = data["email"]
        print("sending subject code", subject_code, email)
        send_mail(
            "Motor Learning App - Subject Code",
            f"Your generated subject code for motor learning experiments is {subject_code}. Save it, because it will be asked for future experiments.\n\nBest,\n\nMotor Learning App Team",
            "lhcubillos93@gmail.com",
            [email],
        )

    return JsonResponse({})


def loaderio(request):
    # Output csv
    response = HttpResponse(content_type="text/plain")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="loaderio-0e64c936e385b2eed7c32769fccfbffd.txt"'
    response.write("loaderio-0e64c936e385b2eed7c32769fccfbffd")
    return response


def handler404(request, exception, template_name="gestureApp/404.html"):
    response = render(request, "gestureApp/404.html", {})
    response.status_code = 404
    return response
