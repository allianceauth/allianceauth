from allianceauth.services.hooks import MenuItemHook, UrlHook

from allianceauth import hooks
from . import urls


class FleetUpMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Fleet-Up',
                              'fa fa-arrow-up fa-fw',
                              'fleetup:view',
                              navactive=['fleetup:'])

    def render(self, request):
        if request.user.has_perm('auth.view_fleetup'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return FleetUpMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'fleetup', r'^fleetup/')
