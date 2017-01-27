# IPBoard3

Add `services.modules.ipboard` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

You’re on your own for the initial install of IPBoard. It’s pretty much just download, unzip, and move to `/var/www/ipboard/`. Make sure to

    sudo chown -R www-data:www-data /var/www/ipboard

a few times because it’s pretty finicky.

You’ll need to add another alias in your apache config, this one for `/ipboard` pointing to `/var/www/ipboard` and add another `<directory>` block for `/var/www/ipboard` with `Require all granted` or `Allow from all` depending on your apache version.

IPBoard needs a database table. Log in to mysql and run:

    create database alliance_ipboard;

That’s all for SQL work. Control+D to close.

Navigate to http://example.com/ipboard and proceed with the install. If it whines about permissions make sure to `chown` again. Point it at that database we just made, using the `allianceserver` MySQL user account from the full install.

Once you get everything installed we need to copy the api module folder

    sudo cp -a /home/allianceserver/allianceauth/thirdparty/IPBoard3/aa /var/www/ipboard/interface/board/modules/aa

and again run that `chown` command.

Log into the AdminCP for IPBoard and find your way to the `System` tab. On the left navigation bar, under `Tools and Settings`, select `API Users`.

Enable the API by toggling the `XML-RPC Status` from `disabled` to `enabled` (red box, top right of the page) and save. Now create a new api user. Put something descriptive for title such as ‘AllianceAuth’, then on the bottom panel click the `AllianceAuth` tab and tick all the boxes. Press `Create New API User` to save it.

Copy the API key. Now edit your settings.py as follows:

 - IPBOARD_APIKEY is the key you just copied
 - IPBOARD_ENDPOINT is `http://example.com/ipboard/interface/board/index.php`

Now enable IPBoard for Auth and/or Blue by editing the auth settings.

Save and exit. Restart apache or gunicorn.

Test it by creating a user through Alliance Auth. Just note right now there’s no real error handling, so if account creation fails it’ll still return a username/password combo.

Good luck!
