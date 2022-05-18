from django.urls import path, re_path
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
    path("profile/create_study", views.create_study, name="create-study"),
    re_path(
        r"^profile/experiment/upload_files/(?P<pk>[A-Z0-9]{4})/$",
        views.upload_files,
        name="upload_files",
    ),
    re_path(
        r"^profile/experiment/edit/(?P<pk>[A-Z0-9]{4})/$",
        views.edit_experiment,
        name="edit_experiment",
    ),
    re_path(
        r"^profile/study/edit/(?P<pk>[A-Z0-9]{4})/$",
        views.edit_study,
        name="edit_study",
    ),
    re_path(r"^experiment/(?P<pk>[A-Z0-9]{4})/$", views.experiment, name="experiment",),
    re_path(r"^study/(?P<pk>[A-Z0-9]{4})/$", views.study, name="study",),
    # path("prep_screen/", views.preparation_screen, name="prep_screen"),
    path("raw_data/", views.download_raw_data, name="download_raw_data"),
    path(
        "processed_data/", views.download_processed_data, name="download_processed_data"
    ),
    # API
    path("api/create_trials", views.create_trials, name="create_trials"),
    path("api/create_subject", views.create_subject, name="create_subject"),
    path("api/send_subject_code", views.send_subject_code, name="send_subject_code"),
    path("api/current_user", views.current_user, name="current_user"),
    path("api/user_experiments", views.user_experiments, name="user_experiments"),
    path("api/user_studies", views.user_studies, name="user_studies"),
    re_path(
        r"^api/experiment/delete/(?P<pk>[A-Z0-9]{4})/$",
        views.delete_experiment,
        name="experiment_delete",
    ),
    re_path(
        r"^api/experiment/disable/(?P<pk>[A-Z0-9]{4})/$",
        views.disable_experiment,
        name="experiment_disable",
    ),
    re_path(
        r"^api/experiment/enable/(?P<pk>[A-Z0-9]{4})/$",
        views.enable_experiment,
        name="experiment_enable",
    ),
    re_path(
        r"^api/experiment/duplicate/(?P<pk>[A-Z0-9]{4})/$",
        views.duplicate_experiment,
        name="experiment_duplicate",
    ),
    re_path(
        r"^api/study/delete/(?P<pk>[A-Z0-9]{4})/$",
        views.delete_study,
        name="study_delete",
    ),
    re_path(
        r"^api/group/delete/(?P<pk>[A-Z0-9]{4})/$",
        views.delete_group,
        name="group_delete",
    ),
    re_path(
        r"^api/group/enable/(?P<pk>[A-Z0-9]{4})/$",
        views.enable_group,
        name="group_enable",
    ),
    re_path(
        r"^api/group/disable/(?P<pk>[A-Z0-9]{4})/$",
        views.disable_group,
        name="group_disable",
    ),
    re_path(
        r"^api/study/disable/(?P<pk>[A-Z0-9]{4})/$",
        views.disable_study,
        name="study_disable",
    ),
    re_path(
        r"^api/study/enable/(?P<pk>[A-Z0-9]{4})/$",
        views.enable_study,
        name="study_enable",
    ),
    re_path(
        r"^api/study/publish/(?P<pk>[A-Z0-9]{4})/$",
        views.publish_study,
        name="study_publish",
    ),
    re_path(
        r"^api/study/duplicate/(?P<pk>[A-Z0-9]{4})/$",
        views.duplicate_study,
        name="study_duplicate",
    ),
    re_path(
        r"^api/experiment/end_survey/(?P<pk>[A-Z0-9]{4})/$",
        views.end_survey,
        name="end_survey",
    ),
    # re_path(
    #     r"^api/experiment/bonstrup_metrics/(?P<pk>[A-Z0-9]{4})/$",
    #     views.download_bonstrup_processed,
    #     name="bonstrup_metrics",
    # ),
    re_path(
        r"^api/experiment/download_end_survey/(?P<pk>[A-Z0-9]{4})/$",
        views.download_survey,
        name="download_survey",
    ),
    path("api/group/new/", views.new_group, name="new_group",),
    path(
        "api/cloud_process_data", views.cloud_process_data, name="cloud_process_data",
    ),
]

