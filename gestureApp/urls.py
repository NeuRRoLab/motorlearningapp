from django.urls import path
from django.contrib.auth.views import LoginView, logout_then_login
from django.urls import reverse_lazy

from . import views

app_name = "gestureApp"
urlpatterns = [
    path("", views.home, name="home"),
    path(
        "login",
        LoginView.as_view(
            template_name="gestureApp/login.html",
            success_url=reverse_lazy("gestureApp:profile"),
        ),
        name="login",
    ),
    path("logout", logout_then_login, name="logout"),
    path("register", views.SignUpView.as_view(), name="register"),
    path("profile", views.Profile.as_view(), name="profile"),
    path(
        "profile/create_experiment", views.create_experiment, name="create-experiment"
    ),
    path("experiment/", views.experiment, name="experiment"),
    path("prep_screen/", views.preparation_screen, name="prep_screen"),
    path("raw_data/", views.download_raw_data, name="download_raw_data"),
    path(
        "processed_data/", views.download_processed_data, name="download_processed_data"
    ),
    # Test
    path(
        "experiment_create", views.ExperimentCreate.as_view(), name="experiment_create"
    ),
    # API
    path("api/create_trials", views.create_trials, name="create_trials"),
    path("api/current_user", views.current_user, name="current_user"),
    path("api/user_experiments", views.user_experiments, name="user_experiments"),
]

