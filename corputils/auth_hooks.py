from services.hooks import MenuItemHook, UrlHook
from alliance_auth import hooks
from corputils import urls


class CorpStats(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Corporation Stats',
                              'fa fa-share-alt fa-fw grayiconecolor',
                              'corputils:view',
                              navactive=['corputils:'])

    def render(self, request):
        if request.user.has_perm('corputils.view_corp_corpstats') or request.user.has_perm('corputils.view_alliance_corpstats') or request.user.has_perm('corputils.add_corpstats'):
                return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return CorpStats()


class CorpStatsUrl(UrlHook):
    def __init__(self):
        UrlHook.__init__(self, urls, 'corputils', r'^corpstats/')


@hooks.register('url_hook')
def register_url():
    return CorpStatsUrl()
