from django.conf.urls import url
import srp.views

app_name = 'srp'

urlpatterns = [
    # SRP URLS
    url(r'^$', srp.views.srp_management, name='management'),
    url(r'^all/$', srp.views.srp_management_all, name='all'),
    url(r'^(\w+)/view$', srp.views.srp_fleet_view, name='fleet'),
    url(r'^add/$', srp.views.srp_fleet_add_view, name='add'),
    url(r'^(\w+)/edit$', srp.views.srp_fleet_edit_view, name='edit'),
    url(r'^(\w+)/request', srp.views.srp_request_view, name='request'),

    # SRP URLS
    url(r'^(\w+)/remove$', srp.views.srp_fleet_remove, name='remove'),
    url(r'^(\w+)/disable$', srp.views.srp_fleet_disable, name='disable'),
    url(r'^(\w+)/enable$', srp.views.srp_fleet_enable, name='enable'),
    url(r'^(\w+)/complete$', srp.views.srp_fleet_mark_completed,
        name='mark_completed'),
    url(r'^(\w+)/incomplete$', srp.views.srp_fleet_mark_uncompleted,
        name='mark_uncompleted'),
    url(r'^request/remove/', srp.views.srp_request_remove,
        name="request_remove"),
    url(r'request/approve/', srp.views.srp_request_approve,
        name='request_approve'),
    url(r'request/reject/', srp.views.srp_request_reject,
        name='request_reject'),
    url(r'^request/(\w+)/update', srp.views.srp_request_update_amount,
        name="request_update_amount"),
    ]