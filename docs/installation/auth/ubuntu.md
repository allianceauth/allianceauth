# Ubuntu Installation

It’s recommended to update all packages before proceeding.

    sudo apt-get update
    sudo apt-get upgrade
    sudo reboot

Now install all [dependencies](dependencies.md).

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

Now we need to make the requisite database.

    create database alliance_auth;
    
    
Create a Python virtual environment and put it somewhere convenient (e.g. `~/venv/aauth/`)

    python3 -m venv /path/to/new/virtual/environment

A virtual environment provides support for creating a lightweight "copy" of Python with their own site directories. Each virtual environment has its own Python binary (allowing creation of environments with various Python versions) and can have its own independent set of installed Python packages in its site directories. You can read more about virtual environments on the [Python docs](https://docs.python.org/3/library/venv.html).
    
Activate the virtualenv using `source /path/to/new/virtual/environment/bin/activate`. Note the `/bin/activate` on the end of the path. Each time you come to do maintenance on your Alliance Auth installation, you should activate your virtual environment first.

Now you can install the library using `pip install allianceauth`. This will install Alliance Auth and all its python dependencies.

Ensure you are in the allianceserver home directory by issuing `cd ~`.

Now you need to create the application that will run the Alliance Auth install.

Issue `django-admin startproject myauth` to bootstrap the Django application that will run Auth. You can rename it from `myauth` anything you'd like, the name is not important for auth.

Grab the example settings file from the [Alliance Auth repository](https://github.com/allianceauth/allianceauth/blob/master/alliance_auth/settings.py.example) for the relevant version you're installing.

The settings file needs configuring. See [this lengthy guide](settings.md) for specifics.

Django needs to install models to the database before it can start.

    python manage.py migrate

Now we need to round up all the static files required to render templates. Answer ‘yes’ when prompted.

    python manage.py collectstatic

Test the server by starting it manually.

    python manage.py runserver 0.0.0.0:8000

If you see an error, stop, read it, and resolve it. If the server comes up and you can access it at `yourip:8000`, you're golden. It's ok to stop the server if you're going to be installing a WSGI server to run it. **Do not use runserver in production!**

Once installed, move onto the [Gunicorn Guide](gunicorn.md) and decide on whether you're going to use [NGINX](nginx.md) or [Apache](apache.md). You will also need to install [supervisor](supervisor.md) to run the background tasks.
