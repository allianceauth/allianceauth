# Openfire

 Openfire is a Jabber (XMPP) server.

## Prepare Your Settings
 - Add `'allianceauth.services.modules.openfire',` to your `INSTALLED_APPS` list
 - Append the following to your auth project's settings file:


    # Jabber Configuration
    JABBER_URL = ""
    JABBER_PORT = 5223
    JABBER_SERVER = ""
    OPENFIRE_ADDRESS = ""
    OPENFIRE_SECRET_KEY = ""
    BROADCAST_USER = ""
    BROADCAST_USER_PASSWORD = ""
    BROADCAST_SERVICE_NAME = "broadcast"

## Dependencies
Openfire require a Java 8 runtime environment.

Ubuntu:

    apt-get install openjdk-8-jdk

CentOS:

    yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel

## Setup
### Download Installer
Openfire is not available through repositories so we need to get a package from the developer.

On your PC, navigate to the [Ignite Realtime downloads section](https://www.igniterealtime.org/downloads/index.jsp), and under Openfire select Linux, click on the Ubuntu: Debian package (second from bottom of list, ends with .deb) or CentOS: RPM Package (no JRE bundled, as we have installed it on the host)

Retrieve the file location by copying the URL from the “click here” link, depending on your browser you may have a Copy Link or similar option in your right click menu.

In the console, ensure you’re in your user’s home directory: `cd ~`

Now download the package. Replace the link below with the link you got earlier.

    wget https://www.igniterealtime.org/downloadServlet?filename=openfire/openfire_4.2.3_all.deb

Now install from the package. Replace the filename with your filename (the last part of the download URL is the file name)

Ubuntu:

    dpkg -i openfire_4.2.3_all.deb

CentOS:

    yum install -y openfire-4.2.3-1.noarch.rpm

### Create Database
Performance is best when working from a SQL database. If you installed MySQL or MariaDB alongside your auth project, go ahead and create a database for Openfire:

    mysql -u root -p
    create database alliance_jabber;
    grant all privileges on alliance_jabber . * to 'allianceserver'@'localhost';
    exit;

### Web Configuration
The remainder of the setup occurs through Openfire’s web interface. Navigate to http://example.com:9090, or if you’re behind CloudFlare, go straight to your server’s IP:9090.

Select your language. I sure hope it’s English if you’re reading this guide.

Under Server Settings, set the Domain to `example.com` replacing it with your actual domain. Don’t touch the rest.

Under Database Settings, select `Standard Database Connection`

On the next page, select `MySQL` from the dropdown list and change the following:
 - `[server]` is replaced by `127.0.0.1`
 - `[database]` is replaced by the name of the database to be used by Openfire
 - enter the login details for your auth project's database user

If Openfire returns with a failed to connect error, re-check these settings. Note the lack of square brackets.

Under Profile Settings, leave `Default` selected.

Create an administrator account. The actual name is irrelevant, just don’t lose this login information.

Finally, log in to the console with your admin account.

Edit your auth project's settings file and enter the values you just set:
 - `JABBER_URL` is the pubic address of your jabber server
 - `JABBER_PORT` is the port for clients to connect to (usually 5223)
 - `JABBER_SERVER` is the name of the jabber server. If you didn't alter it during install it'll usually be your domain (eg `example.com`)
 - `OPENFIRE_ADDRESS` is the web address of Openfire's web interface. Use http:// with port 9090 or https:// with port 9091 if you configure SSL in Openfire

### REST API Setup
Navigate to the `plugins` tab, and then `Available Plugins` on the left navigation bar. You’ll need to fetch the list of available plugins by clicking the link.

Once loaded, press the green plus on the right for `REST API`.

Navigate the `Server` tab, `Sever Settings` subtab. At the bottom of the left navigation bar select `REST API`.

Select `Enabled`, and `Secret Key Auth`. Update your auth project's settings with this secret key as `OPENFIRE_SECRET_KEY`.

### Broadcast Plugin Setup

Navigate to the `Users/Groups` tab and select `Create New User` from the left navigation bar.

Pick a username (e.g. `broadcast`) and password for your ping user. Enter these in your auth project's settings file as `BROADCAST_USER` and `BROADCAST_USER_PASSWORD`. Note that `BROADCAST_USER` needs to be in the format `user@example.com` matching your jabber server name. Press `Create User` to save this user.

Broadcasting requires a plugin. Navigate to the `plugins` tab, press the green plus for the `Broadcast` plugin.

Navigate to the `Server` tab, `Server Manager` subtab, and select `System Properties`. Enter the following:

 - Name: `plugin.broadcast.disableGroupPermissions`
   - Value: `True`
   - Do not encrypt this property value
 - Name: `plugin.broadcast.allowedUsers`
   - Value: `broadcast@example.com`, replacing the domain name with yours
   - Do not encrypt this property value

If you have troubles getting broadcasts to work, you can try setting the optional (you will need to add it) `BROADCAST_IGNORE_INVALID_CERT` setting to `True`. This will allow invalid certificates to be used when connecting to the Openfire server to send a broadcast.

### Preparing Auth

Once all settings are entered, run migrations and restart Gunicorn and Celery.

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
