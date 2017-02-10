from services.hooks import MenuItemHook
from alliance_auth import hooks


class PermissionsTool(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Permissions Audit',
                              'fa fa-key fa-id-card grayiconecolor',
                              'permissions_overview', 400)

    def render(self, request):
        if request.user.has_perm('permissions_tool.audit_permissions'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_util_hook')
def register_menu():
    return PermissionsTool()
