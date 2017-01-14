# phpBB3

## Overview
phpBB is a free php-based forum. It’s the default forum for AllianceAuth.

## Dependencies
All dependencies should have been taken care of during setup.

## Setup
### Download Phpbb3
phpBB is available as a zip from their website. Navigate to the website’s [downloads section](https://www.phpbb.com/downloads/) using your PC browser and copy the URL for the latest version zip.

In the console, navigate to your user’s home directory: `cd ~`

Now download using wget, replacing the url with the url for the package you just retrieved

    wget https://www.phpbb.com/files/release/phpBB-3.2.0.zip

This needs to be unpackaged. Unzip it, replacing the file name with that of the file you just downloaded

    unzip phpBB-3.2.0.zip

Now we need to move this to our web directory. Usually `/var/www/forums`.

    sudo mv phpBB3 /var/www/forums

The web server needs read/write permission to this folder

    sudo chown -R www-data:www-data /var/www/forums

### Web Install
Navigate to http://yourdomain.com/forums where you will be presented with an installer.

Click on the `Install` tab.

All the requirements should be met. Press `Start Install`.

Under Database Settings, set the following:
 - Database Type is `MySQL`
 - Database Server Hostname is `127.0.0.1`
 - Database Server Port is left blank
 - Database Name is `alliance_forum`
 - Database Username is your MySQL user for AllianceAuth, usually `allianceserver`
 - Database Password is this user’s password

You should see `Succesful Connection` and proceed.

Enter administrator credentials on the next page.

Everything from here should be intuitive.

phpBB will then write its own config file.

### Open the Forums
Before users can see the forums, we need to remove the install directory

    sudo rm -rf /var/www/forums/install

### Enabling Avatars
AllianceAuth sets user avatars to their character portrait when the account is created or password reset. We need to allow external URLs for avatars for them to behave properly. Navigate to the admin control panel for phpbb3, and under the `General` tab, along the left navigation bar beneath `Board Configuration`, select `Avatar Settings`. Set `Enable Remote Avatars` to `Yes` and then `Submit`.

![location of the remote avatar setting](http://i.imgur.com/eWrotRX.png)

You can allow members to overwrite the portrait with a custom image if desired. Navigate to `Users and Groups`, `Group Permissions`, select the appropriate group (usually `Member` if you want everyone to have this ability), expand `Advanced Permissions`, under the `Profile` tab, set `Can Change Avatars` to `Yes`, and press `Apply Permissions`.

![location of change avatar setting](http://i.imgur.com/Nc6Rzo9.png)

## Setup Complete
You’ve finished the steps required to make AllianceAuth work with phpBB. Play around with it and make it your own.
