# Apache

## Overview

Alliance Auth gets served using a Web Server Gateway Interface (WSGI) script. This script passes web requests to Alliance Auth which generates the content to be displayed and returns it. This means very little has to be configured in Apache to host Alliance Auth.

If you're using a small VPS to host services with very limited memory, consider using [NGINX](nginx.md).

## Installation

Ubuntu:

    apt-get install apache2

CentOS:

    yum install httpd
    systemctl enable httpd
    systemctl start httpd

## Configuration

Apache serves sites through defined virtual hosts. These are located in `/etc/apache2/sites-available/` on Ubuntu and `/etc/httpd/conf.d/httpd.conf` on CentOS.

A virtual host for auth need only proxy requests to your WSGI server (gunicorn if you followed the install guide) and serve static files. Examples can be found below. Create your config in its own file eg `myauth.conf`.

### Ubuntu

To proxy and modify headers a few mods need to be enabled.

    a2enmod proxy
    a2enmod proxy_http
    a2enmod headers

Create a new config file for auth eg `/etc/apache2/sites-available/myauth.conf` and fill out the virtual host configuration. To enable your config use `a2ensite myauth.conf` and then reload apache with `service apache2 reload`.

### CentOS

Place your virtual host configuration in the appropriate section within `/etc/httpd/conf.d/httpd.conf` and restart the httpd service with `systemctl restart httpd`.

## Sample Config File

```
<VirtualHost *:80>
        ServerName auth.example.com

        ProxyPassMatch ^/static !
        ProxyPass / http://127.0.0.1:8000/
        ProxyPassReverse / http://127.0.0.1:8000/
        ProxyPreserveHost On

        Alias "/static" "/var/www/myauth/static"
        <Directory "/var/www/myauth/static">
            Require all granted
        </Directory>

</VirtualHost>
```

## SSL

It's 2018 - there's no reason to run a site without SSL. The EFF provides free, renewable SSL certificates with an automated installer. Visit their [website](https://certbot.eff.org/) for information.

After acquiring SSL the config file needs to be adjusted. Add the following lines inside the `<VirtualHost>` block:

```
        RequestHeader set X-FORWARDED-PROTOCOL https
        RequestHeader set X-FORWARDED-SSL On
```
