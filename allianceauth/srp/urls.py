from django.conf.urls import url

from . import views

app_name = 'srp'

urlpatterns = [
    # SRP URLS
    url(r'^$', views.srp_management, name='management'),
    url(r'^all/$', views.srp_management, {'all': True}, name='all'),
    url(r'^(\w+)/view$', views.srp_fleet_view, name='fleet'),
    url(r'^add/$', views.srp_fleet_add_view, name='add'),
    url(r'^(\w+)/edit$', views.srp_fleet_edit_view, name='edit'),
    url(r'^(\w+)/request', views.srp_request_view, name='request'),

    # SRP URLS
    url(r'^(\w+)/remove$', views.srp_fleet_remove, name='remove'),
    url(r'^(\w+)/disable$', views.srp_fleet_disable, name='disable'),
    url(r'^(\w+)/enable$', views.srp_fleet_enable, name='enable'),
    url(r'^(\w+)/complete$', views.srp_fleet_mark_completed,
        name='mark_completed'),
    url(r'^(\w+)/incomplete$', views.srp_fleet_mark_uncompleted,
        name='mark_uncompleted'),
    url(r'^request/remove/', views.srp_request_remove,
        name="request_remove"),
    url(r'^request/approve/', views.srp_request_approve,
        name='request_approve'),
    url(r'^request/reject/', views.srp_request_reject,
        name='request_reject'),
    url(r'^request/(\w+)/update', views.srp_request_update_amount,
        name="request_update_amount"),
]
