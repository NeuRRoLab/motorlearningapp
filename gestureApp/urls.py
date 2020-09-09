from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login
from django.urls import reverse_lazy

from . import views

app_name = 'gestureApp'
urlpatterns = [
    path('', views.home, name='home'),
    path('login', LoginView.as_view(
        template_name='gestureApp/login.html',
        success_url=reverse_lazy('gestureApp:profile')), name='login'),
    path('logout', logout_then_login , name='logout'),
    path('register', views.SignUpView.as_view(), name='register'),
    path('profile', views.Profile.as_view(), name='profile'),
    path('profile/create-experiment', views.CreateExperiment.as_view(), name='create-experiment'),
    path('experiment/', views.experiment, name='experiment'),
    path('ajax/create_trials', views.create_trials, name='create_trials')
]