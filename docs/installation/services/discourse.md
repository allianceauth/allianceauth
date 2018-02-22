# Discourse

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.discourse',` to your `INSTALLED_APPS` list 
 - Append the following to your local.py settings file:
 

    # Discourse Configuration
    DISCOURSE_URL = ''
    DISCOURSE_API_USERNAME = ''
    DISCOURSE_API_KEY = ''
    DISCOURSE_SSO_SECRET = ''


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

## Web Server Configuration

You will need to configure your web server to proxy requests to Discourse.

A minimal apache config might look like:

    <VirtualHost *:80>
        ServerName discourse.example.com
        ProxyPass / http://0.0.0.0:7890/
        ProxyPassReverse / http://0.0.0.0:7890/
    </VirtualHost>

A minimal nginx config might look like:

    server {
        listen 80;
        server_name discourse.example.com;
        location / {
            include proxy_params;
            proxy_pass http://127.0.0.1:7890;
        }
    }

## Configure API

### Generate admin account

From the /var/discourse folder,

    ./launcher enter app
    rake admin:create

Follow prompts, being sure to answer `y` when asked to allow admin privileges.

### Create API key

Navigate to `discourse.example.com` and log on. Top right press the 3 lines and select `Admin`. Go to API tab and press `Generate Master API Key`.

Add the following values to your auth project's settings file:
 - `DISCOURSE_URL`: `discourse.example.com` (do not add a trailing slash!)
 - `DISCOURSE_API_USERNAME`: the username of the admin account you generated the API key with
 - `DISCOURSE_API_KEY`: the key you just generated

### Configure SSO

Navigate to `discourse.example.com` and log in. Back to the admin site, scroll down to find SSO settings and set the following:
 - `enable_sso`: True
 - `sso_url`: `http://example.com/discourse/sso`
 - `sso_secret`: some secure key

Save, now set `DISCOURSE_SSO_SECRET` in your auth project's settings file to the secure key you just put in Discourse.

Finally run migrations and restart gunicorn and celery.
