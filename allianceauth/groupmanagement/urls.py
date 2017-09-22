from . import views

from django.conf.urls import include, url
app_name = 'groupmanagement'

urlpatterns = [
    url(r'^groups/', views.groups_view, name='groups'),
    url(r'^group/', include([
        url(r'^management/', views.group_management,
            name='management'),
        url(r'^membership/$', views.group_membership,
            name='membership'),
        url(r'^membership/(\w+)/$', views.group_membership_list,
            name='membership_list'),
        url(r'^membership/(\w+)/remove/(\w+)/$', views.group_membership_remove,
            name='membership_remove'),
        url(r'^request_add/(\w+)', views.group_request_add,
            name='request_add'),
        url(r'^request/accept/(\w+)', views.group_accept_request,
            name='accept_request'),
        url(r'^request/reject/(\w+)', views.group_reject_request,
            name='reject_request'),

        url(r'^request_leave/(\w+)', views.group_request_leave,
            name='request_leave'),
        url(r'leave_request/accept/(\w+)', views.group_leave_accept_request,
            name='leave_accept_request'),
        url(r'^leave_request/reject/(\w+)', views.group_leave_reject_request,
            name='leave_reject_request'),
    ])),
]
