# Teamspeak 3

## Overview
Teamspeak3 is the most popular VOIP program for gamers.

## Dependencies
All dependencies should have been taken care of during the AllianceAuth install.

## Setup
### Download Installer
To install we need a copy of the server. You can find the latest version from [this dl server](http://dl.4players.de/ts/releases/) (I’d recommed getting the latest stable version – find this version number from the [TeamSpeak site](https://www.teamspeak.com/downloads#)). Be sure to get a link to the linux version.

From the console, ensure you’re in the user’s home directory: `cd ~`

And now download the server, replacing the link with the link you got earlier.

    wget http://dl.4players.de/ts/releases/3.0.11.4/teamspeak3-server_linux-amd64-3.0.11.4.tar.gz

Now we need to extract the file.

    tar -xvf teamspeak3-server_linux-amd64-3.0.11.4.tar.gz

### Create User
Teamspeak needs its own user.

    sudo adduser --disabled-login teamspeak

### Install Binary
Now we move the server binary somewhere more accessible and change its ownership to the new user.

    sudo mv teamspeak3-server_linux-amd64 /usr/local/teamspeak

    sudo chown -R teamspeak:teamspeak /usr/local/teamspeak

### Startup
Now we generate a startup script so teamspeak comes up with the server.

    sudo ln -s /usr/local/teamspeak/ts3server_startscript.sh /etc/init.d/teamspeak

    sudo update-rc.d teamspeak defaults

Finally we start the server.

    sudo service teamspeak start

### Update Settings
The console will spit out a block of text. **SAVE THIS**.

Update the AllianceAuth settings file with the following:
 - TEAMSPEAK3_SERVERQUERY_USER is `loginname`
 - TEAMSPEAK3_SERVERQUERY_PASSWORD is `password`

Save and reload apache.

    sudo service apache2 reload

### Generate User Account
And now we can generate ourselves a user account. Navigate to the services in AllianceAuth for your user account and press the checkmark for TeamSpeak 3.

Click the URL provided to automatically connect to our server. It will prompt you to redeem the serveradmin token, enter the `token` from startup.

### Groups

Now we need to make groups. AllianceAuth handles groups in teamspeak differently: instead of creating groups it creates an association between groups in TeamSpeak and groups in AllianceAuth. Go ahead and make the groups you want to associate with auth groups, keeping in mind multiple TeamSpeak groups can be associated with a single auth group.

Navigate back to the AllianceAuth admin interface (yourdomain.com/admin) and under `Services`, select `Auth / TS Groups`. In the top-right corner click `Add`.

The dropdown box provides all auth groups. Select one and assign TeamSpeak groups from the panels below. If these panels are empty, wait a minute for the database update to run.

## Setup Complete
