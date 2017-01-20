# Eve Jacknife

## Overview
Eve Jacknife is used to audit an api so that you might see character skills and what ships they can fly, mails, contracts,assets, and any other given access from a specific api key.

## Dependencies
All php and mysql dependencies should have been taken care of during setup.

## Installation
### Get Code
Navigate to your server's web directory: `cd /var/www`

Download the code: `sudo git clone https://github.com/whinis/eve-jacknife`

### Create Database

    mysql -u root -p -e "create database jackknife; grant all privileges on jackknife.* to 'allianceserver'@'localhost';"

### Configure Settings

Change directory to jacknife: `cd eve-jacknife`

Now copy the template: `sudo cp base.config.php eve.config.php`

And now edit: `sudo nano eve.config.php`

Add the database user information:
 - `$sql_u = "allianceserver"`
 - `$sql_p = "MY_SQL_PASSWORD_HERE"`

## Apache Configuration

Change ownership of the directory: `sudo chown -R www-data:www-data ../eve-jacknife`

Eve Jacknife can be served two ways: on its own subdomain (`jacknife.example.com`) or as an alias (`example.com/jacknife`)

### Subdomain
As its own subdomain, create a new apache config: `sudo nano /etc/apache2/sites-available/jacknife.conf` and enter the following:

    <VirtualHost *:80>
            DocumentRoot "/var/www/eve-jacknife"
            ServerName jacknife.example.com
            <Directory "/var/www/eve-jacknife">
                    Require all granted
                    AllowOverride all
                    DirectoryIndex index.php
            </Directory>
    </VirtualHost>

Enable the new site with `sudo a2ensite jacknife.conf` and then reload apache with `sudo service apache2 reload`

### Alias
As an alias, edit your site config (usually 000-default): `sudo nano etc/apache2/sites-available/000-default.conf` and add the following inside the `VirtualHost` block:

    Alias /jacknife "/var/www/eve-jacknife/"
    <Directory "/var/www/eve-jacknife">
            Require all granted
            DirectoryIndex index.php
    </Directory>

Reload apache to take effect: `sudo service apache2 reload`

## Install SQL

Once apache is configured, Eve Jacknife needs to install some data. Navigate to it in your browser and append `/Installer.php` to the URL.

Enter your database password and press Check. If all the boxes come back green press Save. On the next screen press Install and wait for it to finish.

## Update Auth Settings

Edit your aut settings file (`nano ~/allianceauth/alliance_auth/settings.py`) and replace `API_KEY_AUDIT_URL` with either `jacknife.example.com/?usid={api_id}&apik={vcode}` or `example.com/jacknife/?usid={api_id}&apik={vcode}` depending on your apache choice.
