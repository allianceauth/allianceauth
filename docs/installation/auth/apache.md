# Apache Setup
### Overview

AllianceAuth gets served using a Web Server Gateway Interface (WSGI) script. This script passes web requests to AllianceAuth which generates the content to be displayed and returns it. This means very little has to be configured in Apache to host AllianceAuth.

In the interest of ~~laziness~~ time-efficiency, scroll down for example configs. Use these, changing the ServerName to your domain name.

If you're using a small VPS to host services with very limited memory resources, consider using NGINX with [Gunicorn](gunicorn.md). Even if you would like to use Apache, Gunicorn may give you lower memory usage over mod_wsgi.

### Required Parameters for AllianceAuth Core

The AllianceAuth core requires the following parameters to be set:

    WSGIDaemonProcess
    WSGIProcessGroup
    WSGIScriptAlias

The following aliases are required:

    Alias /static/ to point at the static folder
    Alias /templates/ to point at the templates folder

## Description of Parameters

 - `WSGIDaemonProcess` is the name of the process/application. It also needs to be passed the python-path parameter directing python to search the AllianceAuth directory for modules to load.
 - `WSGIProcessGroup` is the group to run the process under. Typically the same as the name of the process/application.
 - `WSGIScriptAlias` points to the WSGI script.

## Additional Parameters for Full Setup

To pass additional services the following aliases and directories are required:

 - `Alias /forums` to point at the forums folder
 - `Alias /killboard` to point at the killboard

Each of these require directory permissions allowing all connections.

For Apache 2.4 or greater:

    <Directory "/path/to/alias/folder">
        Require all granted
    </Directory>

For Apache 2.3 or older:

    <Directory "/path/to/alias/folder">
        Order Deny,Allow
        Allow from all
    </Directory>

## SSL

You can supply your own SSL certificates if you so desire. The alternative is running behind cloudflare for free SSL.

## Sample Config Files

### Minimally functional config

```
<VirtualHost *:80>
        ServerName example.com
        ServerAdmin webmaster@localhost
 
        DocumentRoot /var/www
 
        WSGIDaemonProcess allianceauth python-path=/home/allianceserver/allianceauth
        WSGIProcessGroup allianceauth
        WSGIScriptAlias / /home/allianceserver/allianceauth/alliance_auth/wsgi.py
 
        Alias /static/ /home/allianceserver/allianceauth/static/
 
        <Directory /home/allianceserver/allianceauth/>
                Require all granted
        </Directory>

        <Directory /var/www/>
                Require all granted
        </Directory>        
</VirtualHost>
```

### Own SSL Cert
 - Apache 2.4 or newer:
   - [000-default.conf](http://pastebin.com/3LLzyNmV)
   - [default-ssl.conf](http://pastebin.com/HUPPEp0R)
 - Apache 2.3 or older:
   - [000-default](http://pastebin.com/HfyKpQNu)
   - [default-ssl](http://pastebin.com/2WCS5jnb)

### No SSL Cloudflare, or LetsEncrypt
 - Apache 2.4 or newer:
   - [000-default.conf](http://pastebin.com/j1Ps3ZK6)
 - Apache 2.3 or older:
   - [000-default](http://pastebin.com/BHQzf2pj)

To have LetsEncrypt automatically install SSL certs, comment out the three lines starting with `WSGI`, install certificates, then uncomment them in `000-default-ls-ssl.conf`

## Enabling and Disabling Sites

To instruct apache to serve traffic from a virtual host, enable it:

    sudo a2ensite NAME
where NAME is the name of the configuration file (eg 000-default.conf)

To disable traffic from a site, disable the virtual host:

    sudo a2dissite NAME
where NAME is the name of the configuration file (eg 000-default.conf)
