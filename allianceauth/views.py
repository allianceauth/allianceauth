from django.views.generic.base import View
from django.http import HttpResponseRedirect


class NightModeRedirectView(View):
    SESSION_VAR = 'NIGHT_MODE'

    def get(self, request, *args, **kwargs):
        request.session[self.SESSION_VAR] = not self.night_mode_state(request)
        return HttpResponseRedirect(request.GET.get('next', '/'))

    @classmethod
    def night_mode_state(cls, request):
        try:
            return request.session.get(cls.SESSION_VAR, False)
        except AttributeError:
            # Session is middleware
            # Sometimes request wont have a session attribute
            return False
