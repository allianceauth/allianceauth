# Openfire

## Overview
Openfire is a java-based xmpp server (jabber).

## Dependencies
One additional package is required - [openjdk8](http://askubuntu.com/questions/464755/how-to-install-openjdk-8-on-14-04-lts)

    sudo add-apt-repository ppa:webupd8team/java -y
    sudo apt-get update
    sudo apt-get install oracle-java8-installer

## Setup
### Download Installer
Openfire is not available through repositories so we need to get a debian from the developer.

On your PC, naviage to the [Ignite Realtime downloads section](https://www.igniterealtime.org/downloads/index.jsp), and under Openfire select Linux, click on the debian file (2nd from bottom of list, ends with .deb).

Retrieve the file location by copying the url from the “click here” link.

In the console, ensure you’re in your user’s home directory: `cd ~`

Now download the package. Replace the link below with the link you got earlier.

    wget https://www.igniterealtime.org/downloadServlet?filename=openfire/openfire_4.1.1_all.deb

Now install from the debian. Replace the filename with your file name (the last part of the download url is the file name)

    sudo dpkg -i openfire_4.1.1_all.deb

### Web Configuration
The remainder of the setup occurs through Openfire’s web interface. Navigate to http://yourdomain.com:9090, or if you’re behind CloudFlare, go straight to your server’s IP:9090.

Select your language. I sure hope it’s english if you’re reading this guide.

Under Server Settings, set the Domain to `yourdomain.com` replacing it with your actual domain. Don’t touch the rest.

Under Database Settings, select `Standard Database Connection`

On the next page, select `MySQL` from the dropdown list and change the following:
 - `[server]` is replaced by `127.0.0.1`
 - `[database]` is replaced by the name of the database to be used by Openfire
 - enter the MySQL username you created for AllianceAuth, usually `allianceserver`
 - enter the MySQL password for this user

If Openfire returns with a failed to connect error, re-check these settings. Note the lack of square brackets.

Under Profile Settings, leave `Default` selected.

Create an administrator account. The actual name is irrelevant, just don’t lost this login information.

Finally, log in to the console with your admin account.

### REST API Setup
Navigate to the `plugins` tab, and then `Available Plugins` on the left navigation bar. You’ll need to fetch the list of available plugins by clicking the link.

Once loaded, press the green plus on the right for `REST API`.

Navigate the `Server` tab, `Sever Settings` subtab. At the bottom of the left navigation bar select `REST API`.

Select `Enabled`, and `Secret Key Auth`. Update Alliance Auth settings with this secret key as `OPENFIRE_SECRET_KEY`.

### Broadcast Plugin Setup

Navigate to the `Users/Groups` tab and select `Create New User` from the left navigation bar.

Username is what you set in `BROADCAST_USER` without the @ sign, usually `broadcast`.

Password is what you set in `BROADCAST_USER_PASSWORD`

Press `Create User` to save this user.

Broadcasting requires a plugin. Navigate to the `plugins` tab, press the green plus for the `Broadcast` plugin.

Navigate to the `Server` tab, `Server Manager` subtab, and select `System Properties`. Enter the following:

 - Name: `plugin.broadcast.disableGroupPermissions`
   - Value: `True`
   - Do not encrypt this property value
 - Name: `plugin.broadcast.allowedUsers`
   - Value: `broadcast@yourdomain.com`, replacing the domain name with yours
   - Do not encrypt this property value

### Group Chat
Channels are available which function like a chat room. Access can be controlled either by password or ACL (not unlike mumble).

Navigate to the `Group Chat` tab and select `Create New Room` from the left navigation bar.
 - Room ID is a short, easy-to-type version of the room’s name users will connect to
 - Room Name is the full name for the room
 - Description is short text describing the room’s purpose
 - Set a password if you want password authentication
 - Every other setting is optional. Save changes.

Now select your new room. On the left navigation bar, select `Permissions`.

ACL is achieved by assigning groups to each of the three tiers: `Owners`, `Admins` and `Members`. `Outcast` is the blacklist. You’ll usually only be assigning groups to the `Member` category.

## Setup Complete
You’ve finished the steps required to make AllianceAuth work with Openfire. Play around with it and make it your own.
