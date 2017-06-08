# URL Hooks

```eval_rst
.. note::
    Currently most URL patterns are statically defined in the project's core urls.py file. Ideally this behaviour will change over time with each module of Alliance Auth providing all of its menu items via the hook. New modules should aim to use the hook over statically adding URL patterns to the project's patterns.
```

The URL hooks allow you to dynamically specify URL patterns from your plugin app or service. To achieve this you should subclass or instantiate the `services.hooks.UrlHook` class and then register the URL patterns with the hook.

To register a UrlHook class you would do the following:

    @hooks.register('url_hook')
    def register_urls():
        return UrlHook(app_name.urls, 'app_name', r^'app_name/')
        
        
The `UrlHook` class specifies some parameters/instance variables required for URL pattern inclusion.

`UrlHook(urls, app_name, base_url)`

#### urls
The urls module to include. See [the Django docs](https://docs.djangoproject.com/en/dev/topics/http/urls/#example) for designing urlpatterns.
#### namespace
The URL namespace to apply. This is usually just the app name.
#### base_url
The URL prefix to match against in regex form. Example `r'^app_name/'`. This prefix will be applied in front of all URL patterns included. It is possible to use the same prefix as existing apps (or no prefix at all) but [standard URL resolution](https://docs.djangoproject.com/en/dev/topics/http/urls/#how-django-processes-a-request) ordering applies (hook URLs are the last ones registered).

### Example

An app called `plugin` provides a single view:

    def index(request):
        return render(request, 'plugin/index.html')

The app's `urls.py` would look like so:

    from django.conf.urls import url
    import plugin.views
    
    urlpatterns = [
        url(r^'index$', plugins.views.index, name='index'),
        ]

Subsequently it would implement the UrlHook in a dedicated `auth_hooks.py` file like so:

    from alliance_auth import hooks
    from services.hooks import UrlHook
    import plugin.urls

    @hooks.register('url_hook')
    def register_urls():
        return UrlHook(plugin.urls, 'plugin', r^'plugin/')

When this app is included in the project's `settings.INSTALLED_APPS` users would access the index view by navigating to `https://example.com/plugin/index`.