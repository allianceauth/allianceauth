from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from alliance_auth.hooks import get_hooks
from authentication.states import MEMBER_STATE, BLUE_STATE
from authentication.models import AuthServicesInfo


class ServicesHook:
    """
    Abstract base class for creating a compatible services
    hook. Decorate with @register('services_hook') to have the
    services module registered for callbacks. Must be in
    auth_hook(.py) sub module
    """
    def __init__(self):
        self.name = 'Undefined'
        self.urlpatterns = []
        self.service_ctrl_template = 'registered/services_ctrl.html'
        self.access_perm = None

    @property
    def title(self):
        """
        A nicely formatted title of the service, for client facing
        display.
        :return: str
        """
        return self.name.title()

    def delete_user(self, user, notify_user=False):
        """
        Delete the users service account, optionally notify them
        that the service has been disabled
        :param user: Django.contrib.auth.models.User
        :param notify_user: Whether the service should sent a
        notification to the user about the disabling of their
        service account.
        :return: True if the service account has been disabled,
        or False if it doesnt exist.
        """
        pass

    def validate_user(self, user):
        pass

    def sync_nickname(self, user):
        """
        Sync the users nickname
        :param user: Django.contrib.auth.models.User
        :return: None
        """
        pass

    def update_groups(self, user):
        """
        Update the users group membership
        :param user: Django.contrib.auth.models.User
        :return: None
        """
        pass

    def update_all_groups(self):
        """
        Iterate through and update all users groups
        :return: None
        """
        pass

    def service_active_for_user(self, user):
        pass

    def show_service_ctrl(self, user, state):
        """
        Whether the service control should be displayed to the given user
        who has the given service state. Usually this function wont
        require overloading.
        :param user: django.contrib.auth.models.User
        :param state: auth user state
        :return: bool True if the service should be shown
        """
        return self.service_active_for_user(user) or user.is_superuser

    def render_services_ctrl(self, request):
        """
        Render the services control template row
        :param request:
        :return:
        """
        return ''

    def __str__(self):
        return self.name or 'Unknown Service Module'

    class Urls:
        def __init__(self):
            self.auth_activate = ''
            self.auth_set_password = ''
            self.auth_reset_password = ''
            self.auth_deactivate = ''

    @staticmethod
    def get_services():
        for fn in get_hooks('services_hook'):
            yield fn()


class MenuItemHook:
    def __init__(self, text, classes, url_name, order=None):
        self.text = text
        self.classes = classes
        self.url_name = url_name
        self.template = 'public/menuitem.html'
        self.order = order if order is not None else 9999

    def render(self, request):
        return render_to_string(self.template,
                                {'item': self},
                                request=request)
