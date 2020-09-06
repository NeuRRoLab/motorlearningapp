from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Experiment, Trial, Subject
from .forms import ExperimentCode
from urllib import parse
import json
from django.utils.timezone import now, make_aware
from django.utils import timezone
from datetime import datetime


# Create your views here.
def experiment(request):
    form = ExperimentCode(request.GET)
    if form.is_valid():
        code = form.cleaned_data['code']
        experiment = get_object_or_404(Experiment, pk=code)
        return render(request, 'gestureApp/experiment.html', {
            'experiment': experiment,
            'blocks': list(experiment.blocks.all().values()),
            'sequences': [block.sequence.sequence for block in experiment.blocks.all()]
            })
    else:
        form = ExperimentCode()
        return render(request, 'gestureApp/home.html', {
            'form':form,
            'error_message': 'Form invalid'
            })
    

def home(request):
    form = ExperimentCode()
    return render(request, 'gestureApp/home.html', {'form':form})

def create_trials(request):
    exp_code = request.POST.get('experiment')
    experiment = get_object_or_404(Experiment, pk=exp_code)
    
    # Create a new subject
    subject = Subject(age=25)
    subject.save()
    # Save the trials to database.
    experiment_trials = json.loads(request.POST.get('experiment_trials'))
    for i,block in enumerate(experiment_trials):
        for trial in block:
            print(make_aware(datetime.fromtimestamp(trial['initial_timestamp']/1000.0)))
            time = (trial['seq_timestamps'][-1]-trial['initial_timestamp'])/1000 if len(trial['seq_timestamps']) > 0 else None
            t = Trial(
                block=experiment.blocks.all()[i],
                subject=subject,
                started_at=make_aware(datetime.fromtimestamp(trial['initial_timestamp']/1000)), 
                did_timeout=False, input_sequence=trial['input_seq'],
                time=time)
            t.save()
    
    # Create response
    data = {}
    return JsonResponse(data)