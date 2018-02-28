# phpBB3

 and run migrations before continuing with this guide to ensure the service is installed.

## Overview
phpBB is a free php-based forum. It’s the default forum for AllianceAuth.

## Dependencies
PHPBB3 requires php installed in your web server. Apache has `mod_php`, NGINX requires `php-fpm`. See [the official guide](https://www.phpbb.com/community/docs/INSTALL.html) for php package requirements.

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.phpbb3',` to your `INSTALLED_APPS` list
 - Append the following to the bottom of the settings file:


    # PHPBB3 Configuration
    PHPBB3_URL = ''
    DATABASES['phpbb3'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_forum',
        'USER': 'allianceserver-phpbb3',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }

## Setup
### Prepare the Database
Create a database to install phpbb3 in.

    mysql -u root -p
    create database alliance_forum;
    grant all privileges on alliance_forum . * to 'allianceserver'@'localhost';
    exit;

Edit your auth project's settings file and fill out the `DATABASES['phpbb3']` part.

### Download Phpbb3
phpBB is available as a zip from their website. Navigate to the website’s [downloads section](https://www.phpbb.com/downloads/) using your PC browser and copy the URL for the latest version zip.

In the console, navigate to your user’s home directory: `cd ~`

Now download using wget, replacing the url with the url for the package you just retrieved

    wget https://www.phpbb.com/files/release/phpBB-3.2.0.zip

This needs to be unpackaged. Unzip it, replacing the file name with that of the file you just downloaded

    unzip phpBB-3.2.0.zip

Now we need to move this to our web directory. Usually `/var/www/forums`.

    sudo mv phpBB3 /var/www/forums

The web server needs read/write permission to this folder

    sudo chown -R www-data:www-data /var/www/forums

### Configuring Web Server
You will need to configure you web server to serve PHPBB3 before proceeding with installation.

A minimal apache config file might look like:

    <VirtualHost *:80>
        ServerName forums.example.com
        DocumentRoot /var/www/forums
        <Directory /var/www/forums>
            Require all granted
            DirectoryIndex index.php
        </Directory>
    </VirtualHost>

A minimal nginx config file might look like:

    server {
        listen 80;
        server_name  forums.example.com;
        root   /var/www/forums;
        index  index.php;
        access_log  /var/logs/forums.access.log;
    
        location ~ /(config\.php|common\.php|cache|files|images/avatars/upload|includes|store) {
            deny all;
            return 403;
        }
    
        location ~* \.(gif|jpe?g|png|css)$ {
            expires   30d;
        }
    
        location ~ \.php$ {
            try_files $uri =404;
            fastcgi_pass   unix:/tmp/php.socket;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include fastcgi_params;
        }
    }

Enter your forum's web address as the `PHPBB3_URL` setting in your auth project's settings file. 

### Web Install
Navigate to your forums web address where you will be presented with an installer.

Click on the `Install` tab.

All the requirements should be met. Press `Start Install`.

Under Database Settings, set the following:
 - Database Type is `MySQL`
 - Database Server Hostname is `127.0.0.1`
 - Database Server Port is left blank
 - Database Name is `alliance_forum`
 - Database Username is your auth MySQL user, usually `allianceserver`
 - Database Password is this user’s password

If you use a table prefix other than the standard `phpbb_` you need to add an additional setting to your auth project's settings file, `PHPBB3_TABLE_PREFIX = ''`, and enter the prefix.

You should see `Succesful Connection` and proceed.

Enter administrator credentials on the next page.

Everything from here should be intuitive.

phpBB will then write its own config file.

### Open the Forums
Before users can see the forums, we need to remove the install directory

    sudo rm -rf /var/www/forums/install

### Enabling Avatars
AllianceAuth sets user avatars to their character portrait when the account is created or password reset. We need to allow external URLs for avatars for them to behave properly. Navigate to the admin control panel for phpbb3, and under the `General` tab, along the left navigation bar beneath `Board Configuration`, select `Avatar Settings`. Set `Enable Remote Avatars` to `Yes` and then `Submit`.

![location of the remote avatar setting](/_static/images/installation/services/phpbb3/avatar_settings.png)

You can allow members to overwrite the portrait with a custom image if desired. Navigate to `Users and Groups`, `Group Permissions`, select the appropriate group (usually `Member` if you want everyone to have this ability), expand `Advanced Permissions`, under the `Profile` tab, set `Can Change Avatars` to `Yes`, and press `Apply Permissions`.

![location of change avatar setting](/_static/images/installation/services/phpbb3/avatar_permissions.png)

### Prepare Auth
Once settings have been configured, run migrations and restart gunicorn and celery.
