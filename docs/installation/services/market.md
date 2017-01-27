# Alliance Market

Add `services.modules.market` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

Alliance Market needs a database. Create one in mysql. Default name is `alliance_market`:

    mysql -u root -p
    create database alliance_market;
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

Edit your apache config. Add the following:

    Alias /market /var/www/evernus-alliance-market/web/

    <Directory "/var/www/evernus-alliance-market/web/">
        DirectoryIndex app.php
        Require all granted
        AllowOverride all
    </Directory>

Enable rewriting

    sudo a2enmod rewrite

Restart apache

    sudo service apache2 reload

Once again, set cache permissions:

    sudo chown -R www-data:www-data app/

Add a user account through auth, then make it a superuser:

    sudo php app/console fos:user:promote your_username --super
