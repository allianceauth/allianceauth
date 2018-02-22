# XenForo

## Overview
[XenForo](https://xenforo.com/) is a popular paid forum. This guide will assume that you already have XenForo installed with a valid license (please keep in mind that XenForo is not free nor open-source, therefore you need to purchase a license first). If you come across any problems related with the installation of XenForo please contact their support service.

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.xenforo',` to your `INSTALLED_APPS` list
 - Append the following to your local.py settings file:


    # XenForo Configuration
    XENFORO_ENDPOINT = 'example.com/api.php'
    XENFORO_DEFAULT_GROUP = 0
    XENFORO_APIKEY   = 'yourapikey'

## XenAPI

By default XenForo does not support any kind of API, however there is a third-party package called [XenAPI](https://github.com/Contex/XenAPI) which provides a simple REST interface by which we can access XenForo's functions in order to create and edit users.

The installation of XenAPI is pretty straight forward. The only thing you need to do is to download the `api.php` from the official repository and upload it in the root folder of your XenForo installation. The final result should look like this:
*forumswebsite.com/***api.php**

Now that XenAPI is installed the only thing left to do is to provide a key.

```php
$restAPI = new RestAPI('REPLACE_THIS_WITH_AN_API_KEY');
```

## Configuration

The settings you created earlier now need to be filled out.

`XENFORO_ENDPOINT` is the address to the API you added. No leading `http://`, but be sure to include the `/api.php` at the end.

`XENFORO_DEFAULT_GROUP` is the ID of the group in XenForo auth users will be added to. Unfortunately XenAPI **cannot create new groups**, therefore you have to create a group manually and then get its ID.

`XENFORO_API_KEY` is the API key value you set earlier.

Once these are entered, run migrations and restart gunicorn and celery.