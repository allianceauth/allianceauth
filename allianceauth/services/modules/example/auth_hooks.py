from django.template.loader import render_to_string

from allianceauth import hooks
from allianceauth.services.hooks import ServicesHook
from .urls import urlpatterns


class ExampleService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.urlpatterns = urlpatterns
        self.service_url = 'http://exampleservice.example.com'
        self.name = 'example'

    """
    Overload base methods here to implement functionality
    """

    def render_services_ctrl(self, request):
        """
        Example for rendering the service control panel row
        You can override the default template and create a
        custom one if you wish.
        :param request:
        :return:
        """
        urls = self.Urls()
        urls.auth_activate = 'auth_example_activate'
        urls.auth_deactivate = 'auth_example_deactivate'
        urls.auth_reset_password = 'auth_example_reset_password'
        urls.auth_set_password = 'auth_example_set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': 'example username'
        }, request=request)


@hooks.register('services_hook')
def register_service():
    return ExampleService()
