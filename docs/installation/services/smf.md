# SMF

## Overview
SMF is a free php-based forum. It’s the one of the forums for AllianceAuth.

## Dependencies
All dependencies should have been taken care of during setup.

## Setup
### Download SMF
Using your browser, you can download the latest version of SMF to your desktop computer. All SMF downloads can be found at SMF Downloads. The latest recommended version will always be available at http://www.simplemachines.org/download/index.php/latest/install/.

In the console, navigate to your user’s home directory: `cd ~`

Now download using wget, replacing the url with the url for the package you just retrieved

    wget http://download.simplemachines.org/index.php?thanks;filename=smf_2-0-13_install.zip

This needs to be unpackaged. Unzip it, replacing the file name with that of the file you just downloaded

    unzip smf_2-0-13_install.zip

Now we need to move this to our web directory. Usually `/var/www/forums`.

    sudo mv smf /var/www/forums

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
 - Database Name is `alliance_smf`
 - Database Username is your MySQL user for AllianceAuth, usually `allianceserver`
 - Database Password is this user’s password

Follow the Directions in the installer.


## Setup Complete
You’ve finished the steps required to make AllianceAuth work with SMF. Play around with it and make it your own.
