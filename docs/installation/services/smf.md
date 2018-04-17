# SMF

## Overview
SMF is a free PHP-based forum.

## Dependencies
SMF requires PHP installed in your web server. Apache has `mod_php`, NGINX requires `php-fpm`. More details can be found in the [SMF requirements page.](https://download.simplemachines.org/requirements.php)

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.smf',` to your `INSTALLED_APPS` list
 - Append the following to the bottom of the settings file:


    # SMF Configuration
    SMF_URL = ''
    DATABASES['smf'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_smf',
        'USER': 'allianceserver-smf',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }

## Setup
### Download SMF
Using your browser, you can download the latest version of SMF to your desktop computer. All SMF downloads can be found at SMF Downloads. The latest recommended version will always be available at http://www.simplemachines.org/download/index.php/latest/install/. Retrieve the file location from the hyperlinked box icon for the zip full install,  depending on your browser you may have a Copy Link or similar option in your right click menu.


Download using wget, replacing the URL with the URL for the package you just retrieved

    wget https://download.simplemachines.org/index.php?thanks;filename=smf_2-0-15_install.zip

This needs to be unpackaged. Unzip it, replacing the file name with that of the file you just downloaded

    unzip smf_2-0-15_install.zip

Now we need to move this to our web directory. Usually `/var/www/forums`.

    sudo mv smf /var/www/forums

The web server needs read/write permission to this folder

Apache: `sudo chown -R www-data:www-data /var/www/forums`  
Nginx: `sudo chown -R nginx:nginx /var/www/forums`

```eval_rst
.. tip::
   Nginx: Some distributions use the ``www-data:www-data`` user:group instead of ``nginx:nginx``. If you run into problems with permissions try it instead.
..
```

### Database Preparation
SMF needs a database. Create one:

    mysql -u root -p
    create database alliance_smf;
    grant all privileges on alliance_smf . * to 'allianceserver'@'localhost';
    exit;

Enter the database information into the `DATABASES['smf']` section of your auth project's settings file.

### Web Server Configuration
Your web server needs to be configured to serve Alliance Market.

A minimal Apache config might look like:

    <VirtualHost *:80>
        ServerName forums.example.com
        DocumentRoot /var/www/forums
        <Directory "/var/www/forums">
            DirectoryIndex index.php
        </Directory>
    </VirtualHost>

A minimal Nginx config might look like:

    server {
        listen 80;
        server_name  forums.example.com;
        root   /var/www/forums;
        index  app.php;
        access_log  /var/logs/forums.access.log;

        location ~ \.php$ {
            try_files $uri =404;
            fastcgi_pass   unix:/tmp/php.socket;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include fastcgi_params;
        }
    }

Enter the web address to your forums into the `SMF_URL` setting in your auth project's settings file.

### Web Install
Navigate to your forums address where you will be presented with an installer.

Click on the `Install` tab.

All the requirements should be met. Press `Start Install`.

Under Database Settings, set the following:
 - Database Type is `MySQL`
 - Database Server Hostname is `127.0.0.1`
 - Database Server Port is left blank
 - Database Name is `alliance_smf`
 - Database Username is your auth MySQL user, usually `allianceserver`
 - Database Password is this user’s password

If you use a table prefix other than the standard `smf_` you need to add an additional setting to your auth project's settings file, `SMF_TABLE_PREFIX = ''`, and enter the prefix.

Follow the directions in the installer.

### Preparing Auth
Once settings are entered, apply migrations and restart Gunicorn and Celery.
