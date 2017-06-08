from services.hooks import MenuItemHook
from alliance_auth import hooks
from services.hooks import ServicesHook


class Services(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self,
                              'Services',
                              'fa fa-cogs fa-fw grayiconecolor',
                              'auth_services', 100)

    def render(self, request):
        for svc in ServicesHook.get_services():
            if svc.service_active_for_user(request.user):
                return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return Services()
