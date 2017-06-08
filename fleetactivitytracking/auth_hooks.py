from services.hooks import MenuItemHook, UrlHook
from alliance_auth import hooks
from fleetactivitytracking import urls


@hooks.register('menu_item_hook')
def register_menu():
    return MenuItemHook('Fleet Activity Tracking', 'fa fa-users fa-lightbulb-o fa-fw grayiconecolor', 'fatlink:view',
                        navactive=['fatlink:'])


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'fatlink', r'^fat/')
