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

    sudo a2enmod proxy_http
    sudo service apache2 reload

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

### Configure SSO

Navigate to `discourse.example.com` and log in. Back to the admin site, scroll down to find SSO settings and set the following:
 - `enable_sso`: True
 - `sso_url`: `http://example.com/discourse/sso`
 - `sso_secret`: some secure key

Save, now change settings.py and add the following:
 - `DISCOURSE_SSO_SECRET`: the secure key you just set

### Enable for your members

Set either or both of `ENABLE_AUTH_DISCOURSE` and `ENABLE_BLUE_DISCOURSE` in settings.py for your members to gain access. Save and exit with control+o, enter, control+x.

## Done
