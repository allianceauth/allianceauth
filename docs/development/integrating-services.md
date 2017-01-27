# Integrating Services

One of the primary roles of Alliance Auth is integrating with external services in order to authenticate and manage users. This is achieved through the use of service modules. 

## The Service Module

Each service module is its own self contained Django app. It will likely contain views, models, migrations and templates. Anything that is valid in a Django app is valid in a service module.

Normally service modules live in `services.modules` though they may also be installed as external packages and installed via `pip` if you wish. A module is installed by including it in the `INSTALLED_APPS` setting.

### Service Module Structure

Typically a service will contain 5 key components:

- [The Hook](#the-hook)
- [The Service Manager](#the-service-manager)
- [The Views](#the-views)
- [The Tasks](#the-tasks)
- [The Models](#the-models)

The architecture looks something like this:

          urls -------▶ Views
           ▲              |
           |              |
           |              ▼
      ServiceHook ----▶ Tasks ----▶ Manager
           ▲
           |
           |
      AllianceAuth
      
      
      Where:
         Module --▶ Dependency/Import

While this is the typical structure of the existing services modules, there is no enforcement of this structure and you are, effectively, free to create whatever architecture may be necessary. A service module need not even communicate with an external service, for example, if similar triggers such as validate_user, delete_user are required for a module it may be convenient to masquerade as a service. Ideally though, using the common structure improves the maintainability for other developers.

### The Hook

In order to integrate with Alliance Auth service modules must provide a `services_hook`. This hook will be a function that returns an instance of the `services.hooks.ServiceHook` class and decorated with the `@hooks.registerhook` decorator. For example:

    @hooks.register('services_hook')
    def register_service():
        return ExampleService()

This would register the ExampleService class which would need to be a subclass of `services.hooks.ServiceHook`.

        
```eval_rst
.. important::
    The hook **MUST** be registered in `yourservice.auth_hooks` along with any other hooks you are registering for Alliance Auth.
```


A subclassed `ServiceHook` might look like this:

    class ExampleService(ServicesHook):
    def __init__(self):
        ServicesHook.__init__(self)
        self.urlpatterns = urlpatterns
        self.service_url = 'http://exampleservice.example.com'

    """
    Overload base methods here to implement functionality
    """


### The ServiceHook class

The base `ServiceHook` class defines function signatures that Alliance Auth will call under certain conditions in order to trigger some action in the service.

You will need to subclass `services.hooks.ServiceHook` in order to provide implementation of the functions so that Alliance Auth can interact with the service correctly. All of the functions are optional, so its up to you to define what you need.

Instance Variables:
- [self.name](#self-name)
- [self.urlpatterns](#self-url-patterns)
- [self.service_ctrl_template](#self-service-ctrl-template)

Properties:
- [title](#title)

Functions:
- [delete_user](#delete-user)
- [validate_user](#validate-user)
- [sync_nickname](#sync-nickname)
- [update_groups](#update-groups)
- [update_all_groups](#update-all-groups)
- [service_enabled_members](#service-enabled-members)
- [service_enabled_blues](#service-enabled-blues)
- [service_active_for_user](#service-active-for-user)
- [show_service_ctrl](#show-service-ctrl)
- [render_service_ctrl](#render-service-ctrl)


#### self.name
Internal name of the module, should be unique amongst modules.

#### self.urlpatterns
You should define all of your service urls internally, usually in `urls.py`. Then you can import them and set `self.urlpatterns` to your defined urlpatterns. 

    from . import urls
    ...
    class MyService(ServiceHook):
        def __init__(self):
            ...
            self.urlpatterns = urls.urlpatterns
            
All of your apps defined urlpatterns will then be included in the `URLconf` when the core application starts.

#### self.service_ctrl_template
This is provided as a courtesy and defines the default template to be used with [render_service_ctrl](#render-service-ctrl). You are free to redefine or not use this variable at all.

#### title
This is a property which provides a user friendly display of your service's name. It will usually do a reasonably good job unless your service name has punctuation or odd capitalisation. If this is the case you should override this method and return a string.

#### delete_user
`def delete_user(self, user, notify_user=False):`

Delete the users service account, optionally notify them that the service has been disabled. The `user` parameter should be a Django User object. If notify_user is set to `True` a message should be set to the user via the `notifications` module to alert them that their service account has been disabled.

The function should return a boolean, `True` if successfully disabled, `False` otherwise.

#### validate_user
`def validate_user(self, user):`

Validate the users service account, deleting it if they should no longer have access. The `user` parameter should be a Django User object.

An implementation will probably look like the following:

        def validate_user(self, user):
        logger.debug('Validating user %s %s account' % (user, self.name))
        if ExampleTasks.has_account(user) and not self.service_active_for_user(user):
            self.delete_user(user, notify_user=True)

No return value is expected.

This function will be called periodically on all users to validate that the given user should have their current service accounts.

#### sync_nickname
`def sync_nickname(self, user):`

Very optional. As of writing only one service defines this. The `user` parameter should be a Django User object. When called, the given users nickname for the service should be updated and synchronised with the service.

If this function is defined, an admin action will be registered on the Django Users view, allowing admins to manually trigger this action for one or many users. The hook will trigger this action user by user, so you won't have to manage a list of users.

#### update_groups
`def update_groups(self, user):`

Update the users group membership. The `user` parameter should be a Django User object. 
When this is called the service should determine the groups the user is a member of and synchronise the group membership with the external service. If you service does not support groups then you are not required to define this.

If this function is defined, an admin action will be registered on the Django Users view, allowing admins to manually trigger this action for one or many users. The hook will trigger this action user by user, so you won't have to manage a list of users.

This action is usually called via a signal when a users group membership changes (joins or leaves a group).

#### update_all_groups
`def update_all_groups(self):`

The service should iterate through all of its recorded users and update their groups.

I'm really not sure when this is called, it may have been a hold over from before signals started to be used. Regardless, it can be useful to server admins who may call this from a Django shell to force a synchronisation of all user groups for a specific service.

#### service_enabled_members
`def service_enabled_members(self):`

Is this service enabled for users with the `Member` state? It should return `True` if the service is enabled for Members, and `False` otherwise. The default is `False`.

An implementation will usually look like:

    def service_enabled_members(self):
        return settings.ENABLE_AUTH_EXAMPLE or False
        
        
```eval_rst
.. note::
    There has been discussion about moving services to permissions based access. You should review `Issue #663 <https://github.com/allianceauth/allianceauth/issues/663/>`_.
```

#### service_enabled_blues
`def service_enabled_blues(self):`

Is this service enabled for users with the `Blue` state? It should return `True` if the service is enabled for Blues, and `False` otherwise. The default is `False`.

An implementation will usually look like:

    def service_enabled_blues(self):
        return settings.ENABLE_BLUE_EXAMPLE or False
        
        
```eval_rst
.. note::
    There has been discussion about moving services to permissions based access. You should review `Issue #663 <https://github.com/allianceauth/allianceauth/issues/663/>`_.
```

#### service_active_for_user
`def service_active_for_user(self, user):`

Is this service active for the given user? The `user` parameter should be a Django User object.

Usually you wont need to override this as it calls `service_enabled_members` or `service_enabled_blues` depending on the users state.

```eval_rst
.. note::
    There has been discussion about moving services to permissions based access. You should review `Issue #663 <https://github.com/allianceauth/allianceauth/issues/663/>`_ as this function will likely need to be defined by each service to check its permission.
```

#### show_service_ctrl
`def show_service_ctrl(self, user, state):`

Should the service be shown for the given `user` with the given `state`? The `user` parameter should be a Django User object, and the `state` parameter should be a valid state from `authentication.states`.

Usually you wont need to override this function.

For more information see the [render_service_ctrl](#render-service-ctrl) section.
 
#### render_service_ctrl
`def render_services_ctrl(self, request):`

Render the services control row. This will be called for all active services when a user visits the `/services/` page and [show_service_ctrl](#show-service-ctrl) returns `True` for the given user.

It should return a string (usually from `render_to_string`) of a table row (`<tr>`) with 4 columns (`<td>`). Column #1 is the service name, column #2 is the users username for this service, column #3 is the services URL, and column #4 is the action buttons.

You may either define your own service template or use the default one provided. The default can be used like this example:

    def render_services_ctrl(self, request):
        """
        Example for rendering the service control panel row
        You can override the default template and create a
        custom one if you wish.
        :param request:
        :return:
        """
        urls = self.Urls()
        urls.auth_activate = 'auth_example_activate'
        urls.auth_deactivate = 'auth_example_deactivate'
        urls.auth_reset_password = 'auth_example_reset_password'
        urls.auth_set_password = 'auth_example_set_password'
        return render_to_string(self.service_ctrl_template, {
            'service_name': self.title,
            'urls': urls,
            'service_url': self.service_url,
            'username': 'example username'
        }, request=request)

the `Urls` class defines the available URL names for the 4 actions available in the default template:

- Activate (create service account)
- Deactivate (delete service account)
- Reset Password (random password)
- Set Password (custom password)

If you don't define one or all of these variable the button for the undefined URLs will not be displayed.

Most services will survive with the default template. If, however, you require extra buttons for whatever reason, you are free to provide your own template as long as you stick within the 4 columns. Multiple rows should be OK, though may be confusing to users.

### Menu Item Hook

If you services needs cannot be satisfied by the Service Control row, you are free to specify extra hooks by subclassing or instantiating the `services.hooks.MenuItemHook` class.

For more information see the [Menu Hooks](menu-hooks.md) page. 

### The Service Manager

The service manager is what interacts with the external service. Ideally it should be completely agnostic about its environment, meaning that it should avoid calls to Alliance Auth and Django in general (except in special circumstances where the service is managed locally, e.g. Mumble). Data should come in already arranged by the Tasks and data passed back for the tasks to manage or distribute.

The reason for maintaining this separation is that managers may be reused from other sources and there may not even be a need to write a custom manager. Likewise, by maintaining this neutral environment others may reuse the managers that we write. It can also significantly ease the unit testing of services.

### The Views

As mentioned at the start of this page, service modules are fully fledged Django apps. This means you're free to do whatever you wish with your views.

Typically most traditional username/password services define four views.

- Create Account
- Delete Account
- Reset Password
- Set Password

These views should interact with the service via the Tasks, though in some instances may bypass the Tasks and access the manager directly where necessary, for example OAuth functionality.


### The Tasks

The tasks component is the glue that holds all of the other components of the service module together. It provides the function implementation to handle things like adding and deleting users, updating groups, validating the existence of a users account. Whatever tasks `auth_hooks` and `views` have with interacting with the service will probably live here.

### The Models

Its very likely that you'll need to store data about a users remote service account locally. As service modules are fully fledged Django apps you are free to create as many models as necessary for persistent storage. You can create foreign keys to other models in Alliance Auth if necessary, though I _strongly_ recommend you limit this to the User and Groups models from `django.contrib.auth.models` and query any other data manually.

If you create models you should create the migrations that go along with these inside of your module/app.


## Examples

There is a bare bones example service included in `services.modules.example`, you may like to use this as the base for your new service.

You should have a look through some of the other service modules before you get started to get an idea of the general structure of one. A lot of them aren't perfect so don't feel like you have to rigidly follow the structure of the existing services if you think its sub-optimal or doesn't suit the external service you're integrating.


## Testing
You will need to add unit tests for all aspects of your service module before it is accepted. Be mindful that you don't actually want to make external calls to the service so you should mock the appropriate components to prevent this behaviour.
