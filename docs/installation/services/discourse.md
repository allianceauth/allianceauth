# Discourse

Add `services.modules.discourse` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

## Install Docker

    wget -qO- https://get.docker.io/ | sh

### Get docker permissions

    sudo usermod -aG docker allianceserver

Logout, then back in for changes to take effect.

## Install Discourse

### Download Discourse

    sudo mkdir /var/discourse
    sudo git clone https://github.com/discourse/discourse_docker.git /var/discourse

### Configure

    cd /var/discourse
    sudo cp samples/standalone.yml containers/app.yml
    sudo nano containers/app.yml

Change the following:
 - `DISCOURSE_DEVELOPER_EMAILS` should be a list of admin account email addresses separated by commas
 - `DISCOUSE_HOSTNAME` should be 127.0.0.1
 - Everything with `SMTP` depends on your mail settings. Account created through auth do not require email validation, so to ignore everything email (NOT RECOMMENDED), just change the SMTP address to something random so it'll install. Note that not setting up email means any password resets emails won't be sent, and auth cannot reset these. [There are plenty of free email services online recommended by Discourse.](https://github.com/discourse/discourse/blob/master/docs/INSTALL-email.md#recommended-email-providers-for-discourse)

To install behind apache, look for this secion:

    ...
    ## which TCP/IP ports should this container expose?
    expose:
      - "80:80"   # fwd host port 80   to container port 80 (http)
    ...

Change it to this:

    ...
    ## which TCP/IP ports should this container expose?
    expose:
      - "7890:80"   # fwd host port 7890   to container port 80 (http)
    ...

Or any other port will do, if taken. Remember this number.

### Build and launch

    sudo nano /etc/default/docker

Uncomment this line:

    DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"

Restart docker:

    sudo service docker restart

Now build:

    sudo ./launcher bootstrap app
    sudo ./launcher start app

#### Errors:
in case you run into not enough RAM for the docker bootstraping you might want to consider using `./discourse-setup` command. It will start bootstraping and is going to create the `/containers/app.yml` which you can edit.
Note: every time you change something in the `app.yml` you must bootstrap again which will take between *2-8 minutes* and is accomplished by `./launcher rebuild app`.

***
## Apache config

Discourse must run on its own subdomain - it can't handle routing behind an alias like '/forums'. To do so, make a new apache config:

    sudo nano /etc/apache2/sites-available/discourse.conf

And enter the following, changing the port if you used a different number:

    <VirtualHost *:80>
        ServerName discourse.example.com
        ProxyPass / http://0.0.0.0:7890/
        ProxyPassReverse / http://0.0.0.0:7890/
    </VirtualHost>

Now enable proxies and restart apache:

    sudo a2ensite discourse
    sudo a2enmod proxy_http
    sudo service apache2 reload

### Setting up SSL

It is 2017 and there is no reason why you should not setup a SSL certificate and enforce https. You may want to consider certbot with Let's encrypt: https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-ubuntu-16-04

    sudo certbot --apache -d example.com

now adapt the apache configuration:

    sudo nano /etc/apache2/sites-enabled/discourse.conf

and adapt it followlingly:

    <VirtualHost *:80>
        ServerName discourse.example.com
        RewriteEngine on
        RewriteCond %{SERVER_NAME} =discourse.example.com
        RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
    </VirtualHost>

Then adapt change the ssl-config file:

    sudo nano /etc/apache2/sites-enabled/discourse-le-ssl.conf

and adapt it followlingly:

    <IfModule mod_ssl.c>
    <VirtualHost *:443>
      ServerName discourse.example.com
      ProxyPass / http://127.0.0.1:7890/
      ProxyPassReverse / http://127.0.0.1:7890/
      ProxyPreserveHost On
      RequestHeader set X-FORWARDED-PROTOCOL https
      RequestHeader set X-FORWARDED-SSL on
      SSLCertificateFile /etc/letsencrypt/live/discourse.example.com/fullchain.pem
      SSLCertificateKeyFile /etc/letsencrypt/live/discourse.example.com/privkey.pem
      Include /etc/letsencrypt/options-ssl-apache.conf
    </VirtualHost>
    </IfModule>

make sure that `a2enmod headers` is enabled and run:

      sudo service apache2 restart

Now you are all set-up and can even enforce https in discourse settings.





## Configure API

### Generate admin account

From the /var/discourse folder,

    ./launcher enter app
    rake admin:create

Follow prompts, being sure to answer `y` when asked to allow admin privileges.

### Create API key

Navigate to `discourse.example.com` and log on. Top right press the 3 lines and select `Admin`. Go to API tab and press `Generate Master API Key`.

Now go to the allianceauth folder and edit settings:

    nano /home/allianceserver/allianceauth/alliance_auth/settings.py

Scroll down to the Discourse section and set the following:
 - `DISCOURSE_URL`: `discourse.example.com`
 - `DISCOURSE_API_USERNAME`: the username of the admin account you generated the API key with
 - `DISCOURSE_API_KEY`: the key you just generated

***
### Configure SSO

Navigate to `discourse.example.com` and log in. Back to the admin site, scroll down to find SSO settings and set the following:
 - `enable_sso`: True
 - `sso_url`: `http://example.com/discourse/sso`
 - `sso_secret`: some secure key

Save, now change settings.py and add the following:
 - `DISCOURSE_SSO_SECRET`: the secure key you just set

### Enable for your members

Assign discourse permissions for each auth-group that should have access to discourse.
You might want to setup Read/Write/Delete rights per Auth group in discourse as you can limit which categories shall be accessablie per auth-group.

## Done
