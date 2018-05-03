from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.utils.translation import ugettext_lazy as _
from allianceauth import hooks
from . import urls


class OpTimerboardMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, _('Fleet Operations'),
                              'fa fa-exclamation  fa-fw',
                              'optimer:view',
                              navactive=['optimer:'])

    def render(self, request):
        if request.user.has_perm('auth.optimer_view'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return OpTimerboardMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'optimer', r'^optimer/')
