from allianceauth.services.hooks import MenuItemHook, UrlHook
from django.utils.translation import ugettext_lazy as _
from allianceauth import hooks
from allianceauth.hrapplications import urls


class ApplicationsMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              _('Applications'),
                              'fa fa-file-o fa-fw',
                              'hrapplications:index',
                              navactive=['hrapplications:'])


@hooks.register('menu_item_hook')
def register_menu():
    return ApplicationsMenu()


class ApplicationsUrls(UrlHook):
    def __init__(self):
        UrlHook.__init__(self, urls, 'hrapplications', r'^hr/')


@hooks.register('url_hook')
def register_url():
    return ApplicationsUrls()
