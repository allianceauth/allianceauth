# Teamspeak 3

Add `services.modules.teamspeak3` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

## Overview
Teamspeak3 is the most popular VOIP program for gamers.

But have you considered using Mumble? Not only is it free, but it has features and performance far superior to Teamspeak3.

## Dependencies
All dependencies should have been taken care of during the AllianceAuth install.

## Setup
Sticking with it? Alright, I tried.

### Download Installer
To install we need a copy of the server. You can find the latest version from [this dl server](http://dl.4players.de/ts/releases/) (I’d recommed getting the latest stable version – find this version number from the [TeamSpeak site](https://www.teamspeak.com/downloads#)). Be sure to get a link to the linux version.

From the console, ensure you’re in the user’s home directory: `cd ~`

And now download the server, replacing the link with the link you got earlier.

    http://dl.4players.de/ts/releases/3.0.13.6/teamspeak3-server_linux_amd64-3.0.13.6.tar.bz2

Now we need to extract the file.

    tar -xf teamspeak3-server_linux_amd64-3.0.13.6.tar.bz2

### Create User
Teamspeak needs its own user.

    sudo adduser --disabled-login teamspeak

### Install Binary
Now we move the server binary somewhere more accessible and change its ownership to the new user.

    sudo mv teamspeak3-server_linux_amd64 /usr/local/teamspeak
    sudo chown -R teamspeak:teamspeak /usr/local/teamspeak

### Startup
Now we generate a startup script so teamspeak comes up with the server.

    sudo ln -s /usr/local/teamspeak/ts3server_startscript.sh /etc/init.d/teamspeak
    sudo update-rc.d teamspeak defaults

Finally we start the server.

    sudo service teamspeak start

### Update Settings
The console will spit out a block of text. **SAVE THIS**.

Update the AllianceAuth settings file with the following from that block of text:
 - `TEAMSPEAK3_SERVERQUERY_USER` is `loginname` (usually `serveradmin`)
 - `TEAMSPEAK3_SERVERQUERY_PASSWORD` is `password`

Save and reload apache. Restart celery workers as well.

    sudo service apache2 reload

If you plan on claiming the ServerAdmin token, do so with a different TeamSpeak client profile than the one used for your auth account, or you will lose your admin status.

### Generate User Account
And now we can generate ourselves a user account. Navigate to the services in AllianceAuth for your user account and press the checkmark for TeamSpeak 3.

Click the URL provided to automatically connect to our server. It will prompt you to redeem the serveradmin token, enter the `token` from startup.

### Groups

Now we need to make groups. AllianceAuth handles groups in teamspeak differently: instead of creating groups it creates an association between groups in TeamSpeak and groups in AllianceAuth. Go ahead and make the groups you want to associate with auth groups, keeping in mind multiple TeamSpeak groups can be associated with a single auth group.

Navigate back to the AllianceAuth admin interface (example.com/admin) and under `Services`, select `Auth / TS Groups`. In the top-right corner click `Add`.

The dropdown box provides all auth groups. Select one and assign TeamSpeak groups from the panels below. If these panels are empty, wait a minute for the database update to run, or see the [troubleshooting section](#ts-group-models-not-populating-on-admin-site) below.

## Troubleshooting

### `Insufficient client permissions (failed on Invalid permission: 0x26)`

Using the advanced permissions editor, ensure the `Guest` group has the permission `Use Privilege Keys to gain permissions` (under `Virtual Server` expand the `Administration` section)

To enable advanced permissions, on your client go to the `Tools` menu, `Application`, and under the `Misc` section, tick `Advanced permission system`

### TS group models not populating on admin site
The method which populates these runs every 30 minutes. To populate manually, start a celery shell:

    celery -A alliance_auth shell

And execute the update:

    run_ts3_group_update()

Ensure that command does not return an error.

### `2564 access to default group is forbidden`

This usually occurs because auth is trying to remove a user from the `Guest` group (group ID 8). The guest group is only assigned to a user when they have no other groups, unless you have changed the default teamspeak server config.

Teamspeak servers v3.0.13 and up are especially susceptible to this. Ensure the Channel Admin Group is not set to `Guest (8)`. Check by right clicking on the server name, `Edit virtual server`, and in the middle of the panel select the `Misc` tab.

### `TypeError: string indices must be integers, not str`

This error generally means teamspeak returned an error message that went unhandled. The full traceback is required for proper debugging, which the logs do not record. Please check the superuser notifications for this record and get in touch with a developer.

### `3331 flood ban`

This most commonly happens when your teamspeak server is externally hosted. You need to add the auth server IP to the teamspeak serverquery whitelist. This varies by provider.

If you have SSH access to the server hosting it, you need to locate the teamspeak server folder and add the auth server IP on a new line in  `server_query_whitelist.txt`

### `520 invalid loginname or password`

The serverquery account login specified in settings.py is incorrect. Please verify `TEAMSPEAK3_SERVERQUERY_USER` and `TEAMSPEAK3_SERVERQUERY_PASSWORD`. The [installation section](#update-settings) describes where to get them.

### `2568 insufficient client permissions`

This usually occurs if you've created a separate serverquery user to use with auth. It has not been assigned sufficient permissions to complete all the tasks required of it. The full list of required permissions is not known, so assign liberally.