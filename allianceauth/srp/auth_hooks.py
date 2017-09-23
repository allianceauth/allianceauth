from allianceauth.services.hooks import MenuItemHook, UrlHook

from allianceauth import hooks
from . import urls


class SrpMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Ship Replacement',
                              'fa fa-money fa-fw',
                              'srp:management',
                              navactive=['srp:'])

    def render(self, request):
        if request.user.has_perm('srp.access_srp'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return SrpMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'srp', r'^srp/')
