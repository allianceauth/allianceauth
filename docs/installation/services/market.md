# Alliance Market

## Dependencies
Alliance Market requires php installed in your web server. Apache has `mod_php`, NGINX requires `php-fpm`.

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.market',` to your `INSTALLED_APPS` list
 - Append the following to the bottom of the settings file


    # Alliance Market
    MARKET_URL = ''
    DATABASES['market'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alliance_market',
        'USER': 'allianceserver-market',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }

## Setup Alliance Market
Alliance Market needs a database. Create one in mysql. Default name is `alliance_market`:

    mysql -u root -p
    create database alliance_market;
    grant all privileges on alliance_market . * to 'allianceserver'@'localhost';
    exit;

To clone the repo, install packages:

    sudo apt-get install mercurial meld

Change to the web folder:

    cd /var/www

Now clone the repo

    sudo hg clone https://bitbucket.org/krojew/evernus-alliance-market

Make cache and log directories

    sudo mkdir evernus-alliance-market/app/cache
    sudo mkdir evernus-alliance-market/app/logs
    sudo chmod -R 777 evernus-alliance-market/app/cache
    sudo chmod -R 777 evernus-alliance-market/app/logs

Change ownership to apache

    sudo chown -R www-data:www-data evernus-alliance-market

Enter

    cd evernus-alliance-market

Set environment variable

    export SYMFONY_ENV=prod

Copy configuration

    sudo cp app/config/parameters.yml.dist  app/config/parameters.yml

Edit, changing the following:
 - `database_name` to `alliance_market`
 - `database_user` to your MySQL user (usually `allianceserver`)
 - `database_password` to your MySQL user password
 - email settings, eg gmail

Edit `app/config/config.yml` and add the following:

    services:
        fos_user.doctrine_registry:
            alias: doctrine

Install composer [as per these instructions.](https://getcomposer.org/download/)

Update dependencies.

    sudo php composer.phar update --optimize-autoloader

Prepare the cache:

    sudo php app/console cache:clear --env=prod --no-debug


Dump assets:

    sudo php app/console assetic:dump --env=prod --no-debug


Create DB entries

    sudo php app/console doctrine:schema:update --force

Install SDE:

    sudo php app/console evernus:update:sde

Configure your web server to serve alliance market.

A minimal apache config might look like:

    <VirtualHost *:80>
        ServerName market.example.com
        DocumentRoot /var/www/evernus-alliance-market/web
        <Directory "/var/www/evernus-alliance-market/web/">
            DirectoryIndex app.php
            Require all granted
            AllowOverride all
        </Directory>
    </VirtualHost>

A minimal nginx config might look like:

    server {
        listen 80;
        server_name  market.example.com;
        root   /var/www/evernus-alliance-market/web;
        index  app.php;
        access_log  /var/logs/market.access.log;
    
        location ~ \.php$ {
            try_files $uri =404;
            fastcgi_pass   unix:/tmp/php.socket;
            fastcgi_index  index.php;
            fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
            include fastcgi_params;
        }
    }

Once again, set cache permissions:

    sudo chown -R www-data:www-data app/

Add a user account through auth, then make it a superuser:

    sudo php app/console fos:user:promote your_username --super

Now edit your auth project's settings file and fill in the web URL to your market as well as the database details.

Finally run migrations and restart gunicorn and celery.