from django.conf.urls import url
import hrapplications.views

app_name = 'hrapplications'

urlpatterns = [
    url(r'^$', hrapplications.views.hr_application_management_view,
        name="index"),
    url(r'^create/$', hrapplications.views.hr_application_create_view,
        name="create_view"),
    url(r'^create/(\d+)', hrapplications.views.hr_application_create_view,
        name="create_view"),
    url(r'^remove/(\w+)', hrapplications.views.hr_application_remove,
        name="remove"),
    url(r'view/(\w+)', hrapplications.views.hr_application_view,
        name="view"),
    url(r'personal/view/(\w+)', hrapplications.views.hr_application_personal_view,
        name="personal_view"),
    url(r'personal/removal/(\w+)',
        hrapplications.views.hr_application_personal_removal,
        name="personal_removal"),
    url(r'approve/(\w+)', hrapplications.views.hr_application_approve,
        name="approve"),
    url(r'reject/(\w+)', hrapplications.views.hr_application_reject,
        name="reject"),
    url(r'search/', hrapplications.views.hr_application_search,
        name="search"),
    url(r'mark_in_progress/(\w+)', hrapplications.views.hr_application_mark_in_progress,
        name="mark_in_progress"),
    ]
