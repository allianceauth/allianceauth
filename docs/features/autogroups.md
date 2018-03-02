# Auto Groups

```eval_rst
.. note::
    New in 2.0
```

Auto groups allows you to automatically place users of certain states into Corp or Alliance based groups. These groups are created when the first user is added to them and removed when the configuration is deleted.


## Installation

Add `'allianceauth.eveonline.autogroups',` to your `INSTALLED_APPS` list and run migrations. All other settings are controlled via the admin panel under the `Eve_Autogroups` section.


## Configuring a group

When you create an autogroup config you will be given the following options:

![Create Autogroup page](/_static/images/features/autogroups/group-creation.png)

```eval_rst
.. warning::
    After creating a group you wont be able to change the Corp and Alliance group prefixes, name source and the replace spaces settings. Make sure you configure these the way you want before creating the config. If you need to change these you will have to create a new autogroup config.
```

- States selects which states will be added to automatic corp/alliance groups

- Corp/Alliance groups checkbox toggles corp/alliance autogroups on or off for this config.

- Corp/Alliance group prefix sets the prefix for the group name, e.g. if your corp was called `MyCorp` and your prefix was `Corp `, your autogroup name would be created as `Corp MyCorp`. This field accepts leading/trailing spaces.

- Corp/Alliance name source sets the source of the corp/alliance name used in creating the group name. Currently the options are Full name and Ticker.

- Replace spaces allows you to replace spaces in the autogroup name with the value in the Replace spaces with field. This can be blank.
