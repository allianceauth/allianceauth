# Mumble

## Prepare Your Settings
In your auth project's settings file, do the following:
 - Add `'allianceauth.services.modules.mumble',` to your `INSTALLED_APPS` list
 - Append the following to your local.py settings file:


    # Mumble Configuration
    MUMBLE_URL = ""

## Overview
Mumble is a free voice chat server. While not as flashy as TeamSpeak, it has all the functionality and is easier to customize. And is better. I may be slightly biased.

## Dependencies
The mumble server package can be retrieved from a repository we need to add, mumble/release.

    sudo apt-add-repository ppa:mumble/release
    sudo apt-get update

Now two packages need to be installed:

    sudo apt-get install python-software-properties mumble-server

Download the appropriate authenticator release from https://github.com/allianceauth/mumble-authenticator and install the python dependencies for it:

    pip install -r requirements.txt

## Configuring Mumble
Mumble ships with a configuration file that needs customization. By default it’s located at /etc/mumble-server.ini. Open it with your favourite text editor:

    sudo nano /etc/mumble-server.ini

REQUIRED: To enable the ICE authenticator, edit the following:

 - `icesecretwrite=MY_CLEVER_PASSWORD`, obviously choosing a secure password

By default mumble operates on SQLite which is fine, but slower than a dedicated MySQL server. To customize the database, edit the following:

 - uncomment the database line, and change it to `database=alliance_mumble`
 - `dbDriver=QMYSQL`
 - `dbUsername=allianceserver` or whatever you called the Alliance Auth MySQL user
 - `dbPassword=` that user’s password
 - `dbPort=3306`
 - `dbPrefix=murmur_`

To name your root channel, uncomment and set `registerName=` to whatever cool name you want

Save and close the file (control + O, control + X).

To get Mumble superuser account credentials, run the following:

    sudo dpkg-reconfigure mumble-server

Set the password to something you’ll remember and write it down. This is needed to manage ACLs.

Now restart the server to see the changes reflected.

    sudo service mumble-server restart

That’s it! Your server is ready to be connected to at example.com:64738

## Configuring the Authenticator

The ICE authenticator lives in the mumble-authenticator repository, cd to the directory where you cloned it.

Make a copy of the default config:

    cp authenticator.ini.example authenticator.ini

Edit `authenticator.ini` and change these values:

 - `[database]`
   - `user = ` your allianceserver MySQL user
   - `password = ` your allianceserver MySQL user's password
 - `[ice]`
   - `secret = ` the `icewritesecret` password set earlier

Test your configuration by starting it: `python authenticator.py`

## Running the Authenticator

The authenticator needs to be running 24/7 to validate users on Mumble. You should check the [supervisor docs](../auth/supervisor.md) on how to achieve this.

Note that groups will only be created on Mumble automatically when a user joins who is in the group.

## Making and Managing Channels
ACL is really above the scope of this guide. Once Alliance Auth creates your groups, go ahead and follow one of the wonderful web guides available on how to set up channel ACL properly.

## Prepare Auth
In your project's settings file, set `MUMBLE_URL` to the public address of your mumble server. Do not include any leading `http://` or `mumble://`.

Run migrations and restart Gunicorn and Celery to complete setup.
