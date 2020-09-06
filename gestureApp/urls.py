from django.urls import path

from . import views

app_name = 'gestureApp'
urlpatterns = [
    path('', views.home, name='home'),
    path('experiment/', views.experiment, name='experiment'),
    path('ajax/create_trials', views.create_trials, name='create_trials')
]