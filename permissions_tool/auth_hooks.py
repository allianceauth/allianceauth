from services.hooks import MenuItemHook, UrlHook
from alliance_auth import hooks
from permissions_tool import urls


class PermissionsTool(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Permissions Audit',
                              'fa fa-key fa-id-card grayiconecolor',
                              'permissions_tool:overview',
                              order=400,
                              navactive=['permissions_tool:'])

    def render(self, request):
        if request.user.has_perm('permissions_tool.audit_permissions'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return PermissionsTool()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'permissions_tool', r'^permissions/')
