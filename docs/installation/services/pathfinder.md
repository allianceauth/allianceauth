# Pathfinder
Pathfinder is a wormhole mapping tool.

While auth doesn't integrate with pathfinder anymore, from personal experience I've found it much easier to use the following install process than to try and follow the pathfinder-supplied docs.


## Installation
### Get the code

Navigate to the install location: `cd /var/www/` and git clone the repo: 

    sudo git clone https://github.com/exodus4d/pathfinder.git

### Create logs and caches

Change directory to pathfinder: `cd pathfinder`

The logging and caching folders need to be created and have permission set. If upon installation you get Server Error 500, try resetting these permissions.

    sudo mkdir logs
    sudo mkdir tmp/cache
    sudo chmod -R 766 logs
    sudo chmod -R 766 tmp/cache

## .htaccess Configuration

In your `pathfinder` directory there are two `.htaccess` files. The default installation instructions want you to choose one for rewriting purposes, and these force you to www.pathfinder.example.com. Personally I don't like that.

So we'll frankenstein our own. We'll use the HTTP one as a base: 

    sudo mv .htaccess .htaccess_HTTPS
    sudo mv .htaccess_HTTPS .htaccess
    sudo nano .htaccess

Find the www rewriting section (labelled `Rewrite NONE www. to force www.`). Change it so that all lines start with a `#`:

    #RewriteCond %{HTTP_HOST} !^www\.
    # skip "localhost" (dev environment)...
    #RewriteCond %{HTTP_HOST} !=localhost
    # skip IP calls (dev environment) e.g. 127.0.0.1
    #RewriteCond %{HTTP_HOST} !^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$
    # rewrite everything else to "http://" and "www."
    #RewriteRule .* http://www.%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

This allows us to choose SSL and www forwarding with our apache conf instead of this htaccess file.

## Apache Configuration
The best way to have this is to setup a subdomain on your server.

Create a config file `sudo nano /etc/apache2/sites-available/pathfinder.conf` and enter [this configuration](http://pastebin.com/wmXyf6pN), being sure to edit the `ServerName`

Enable it with:

    sudo a2ensite pathfinder.conf
    sudo service apache2 reload

## Configuration Files 

The default configuration should be fine in most cases. Edit all values with caution!

environment.ini
 - `SERVER` Should be changed to `PRODUCTION`
 - `BASE`  is the full filesystem path to the application root on your server. In our case, `/var/www/pathfinder/`
 - `URL`  Is the URL to your app (without a trailing slash). In our case, `http://pathfinder.example.com`
 - `DEBUG` sets the level of debugging (1,2 or 3) (check  /logs  for a more detail backtrace information) 
 - `DB_*` sets your DB connection information 
 - `SMTP_*`  are used to send out emails, you will need an SMTP server login to make this work. (not required)
 - `SSO_CCP_*` follow the [official docs](https://github.com/exodus4d/pathfinder/wiki/CREST)

## Database Setup
This is done through the browser. Go to `pathfinder.example.com/setup` and see the [official docs](https://github.com/exodus4d/pathfinder/wiki/Database) for instructions.

## Cron Jobs 
Again the [official docs](https://github.com/exodus4d/pathfinder/wiki/Cronjob) do a good job here.

## Finish Setup
Once you've compelted the above steps, we need to disable the setup page. Edit the routes with `nano app/routes.ini` and put a `;` in front of the line starting with `GET @setup`