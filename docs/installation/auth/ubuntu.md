# Ubuntu Installation

It’s recommended to update all packages before proceeding.

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot

Now install all [dependencies](dependencies.md). For this guide you'll need the optional [Apache section](dependencies.md) as well.

    sudo apt-get install xxxxxxx
replacing the xs with the list of packages.

For security and permissions, it’s highly recommended you create a user to install under who is not the root account.

    sudo adduser allianceserver

This user needs sudo powers. Add them by editing the sudoers file:

    sudo nano /etc/sudoers

Find the line which says `root ALL=(ALL:ALL) ALL` - beneath it add another line `allianceserver ALL=(ALL:ALL) ALL` - now reboot.

**From this point on you need to be logged in as the allianceserver user**

AllianceAuth needs a MySQL user account. Create one as follows, replacing `PASSWORD` with an actual secure password:

    mysql -u root -p
    CREATE USER 'allianceserver'@'localhost' IDENTIFIED BY 'PASSWORD';
    GRANT ALL PRIVILEGES ON * . * TO 'allianceserver'@'localhost';

Now we need to make the requisite databases.

    create database alliance_auth;
    create database alliance_forum;
    create database alliance_jabber;
    create database alliance_mumble;

Ensure you are in the allianceserver home directory by issuing `cd`

Now we clone the source code:

    git clone https://github.com/allianceauth/allianceauth.git

Enter the folder by issuing `cd allianceauth`

Ensure you're on the latest version with the following:

    git tag | sort -n | tail -1 | xargs git checkout

Python package dependencies can be installed from the requirements file:

    sudo pip install -r requirements.txt

The settings file needs configuring. See [this lengthy guide](settings.md) for specifics.

Django needs to install models to the database before it can start.

    python manage.py migrate

AllianceAuth needs to generate corp and alliance models before it can assign users to them.

    python manage.py shell < run_alliance_corp_update.py

Now we need to round up all the static files required to render templates. Answer ‘yes’ when prompted.

    python manage.py collectstatic

Test the server by starting it manually.

    python manage.py runserver 0.0.0.0:8000

If you see an error, stop, read it, and resolve it. If the server comes up and you can access it at `yourip:8000`, you're golden. It's ok to stop the server if you're going to be installing apache.

Once installed, follow the [Quick Start Guide](quickstart.md)
