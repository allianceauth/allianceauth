# Menu Hooks

```eval_rst
.. note::
    Currently most menu items are statically defined in the `base.html` template. Ideally this behaviour will change over time with each module of Alliance Auth providing all of its menu items via the hook. New modules should aim to use the hook over statically adding menu items to the base template.
```

The menu hooks allow you to dynamically specify menu items from your plugin app or service. To achieve this you should subclass or instantiate the `services.hooks.MenuItemHook` class and then register the menu item with one of the hooks.

There are three levels of Menu Item Hooks

- `menu_main_hook`
- `menu_aux_hook`
- `menu_util_hook`

These represent the 3 levels of menu displayed on the site.

To register a MenuItemHook class you would do the following:

    @hooks.register('menu_util_hook')
    def register_menu():
        return MenuItemHook('Example Item', 'glyphicon glyphicon-heart', 'example_url_name', 150)
        
        
The `MenuItemHook` class specifies some parameters/instance variables required for menu item display.

`MenuItemHook(text, classes, url_name, order=None)`

#### text
The text value of the link
#### classes
The classes that should be applied to the bootstrap menu item icon
#### url_name
The name of the Django URL to use
#### order
An integer which specifies the order of the menu item, lowest to highest

If you cannot get the menu item to look the way you wish, you are free to subclass and override the default render function and the template used.
