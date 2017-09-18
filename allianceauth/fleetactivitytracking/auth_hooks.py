from . import urls

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook


@hooks.register('menu_item_hook')
def register_menu():
    return MenuItemHook('Fleet Activity Tracking', 'fa fa-users fa-lightbulb-o fa-fw grayiconecolor', 'fatlink:view',
                        navactive=['fatlink:'])


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'fatlink', r'^fat/')
