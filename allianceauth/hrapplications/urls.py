from django.conf.urls import url

from . import views

app_name = 'hrapplications'

urlpatterns = [
    url(r'^$', views.hr_application_management_view,
        name="index"),
    url(r'^create/$', views.hr_application_create_view,
        name="create_view"),
    url(r'^create/(\d+)', views.hr_application_create_view,
        name="create_view"),
    url(r'^remove/(\w+)', views.hr_application_remove,
        name="remove"),
    url(r'^view/(\w+)', views.hr_application_view,
        name="view"),
    url(r'^personal/view/(\w+)', views.hr_application_personal_view,
        name="personal_view"),
    url(r'^personal/removal/(\w+)',
        views.hr_application_personal_removal,
        name="personal_removal"),
    url(r'^approve/(\w+)', views.hr_application_approve,
        name="approve"),
    url(r'^reject/(\w+)', views.hr_application_reject,
        name="reject"),
    url(r'^search/', views.hr_application_search,
        name="search"),
    url(r'^mark_in_progress/(\w+)', views.hr_application_mark_in_progress,
        name="mark_in_progress"),
    ]
