# XenForo

Add `services.modules.xenforo` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

In this chapter we will explore how to setup AllianceAuth to work with [XenForo](https://xenforo.com/). At this point we will assume that you already have XenForo installed with a valid license (please keep in mind that XenForo is not free nor open-source, therefore you need to purchase a license first). If you come across any problems related with the installation of XenForo please contact their support service.


## XenAPI

By default XenForo does not support any kind of API, however there is a third-party package called [XenAPI](https://github.com/Contex/XenAPI) which provides a simple REST interface by which we can access XenForo's functions in order to create and edit users.

The installation of XenAPI is pretty straight forward. The only thing you need to do is to download the `api.php` from the official repository and upload it in the root folder of your XenForo installation. The final result should look like this:
*forumswebsite.com/***api.php**

Now that XenAPI is installed the only thing left to do is to provide a key.

```php
$restAPI = new RestAPI('REPLACE_THIS_WITH_AN_API_KEY');
```

## Configuration

AllianceAuth only needs to know 3 things about XenForo.

+ The API Endpoint
+ The API Key
+ The default group

The first two should be self explanatory. The default group is where AllianceAuth will add the user once his account is created. Unfortunately XenAPI **cannot create new groups**, therefore you have to create a group manually and then get its ID.

When you have a forum section which should be accessible ONLY by the auth'd users the access settings must be set to the default group.

In the future we will have different groups for blues and alliance/corp members.
