# Alliance Auth Installation

```eval_rst
.. tip::
   Installation is easiest as the root user. Log in as root or a user with sudo powers.
```

## Dependencies

Alliance Auth can be installed on any operating system. Dependencies are provided below for two of the most popular server platforms, Ubuntu and CentOS. To install on your favourite flavour of linux, identify and install equivalent packages to the ones listed here.

```eval_rst
.. hint::
   CentOS: A few packages are included in a non-default repository. Add it and update the package lists. ::
   
      yum -y install https://centos7.iuscommunity.org/ius-release.rpm
      yum update
```

### Python

Alliance Auth requires python3.4 or higher. Ensure it is installed on your server before proceeding.

Ubuntu:

    apt-get install python3 python3-dev python3-venv python3-setuptools python3-pip

CentOS:

    yum install python36u python36u-devel python36u-setuptools python36u-pip

### Database

It's recommended to use a database service instead of sqlite. Many options are available, but this guide will use MariaDB.

Ubuntu:

    apt-get install mariadb-server mysql-client libmysqlclient-dev

CentOS:

    yum install mariadb-server mariadb-devel mariadb

### Redis and Other Tools

A few extra utilities are also required for installation of packages.

Ubuntu:

    apt-get install unzip git redis-server curl libssl-dev libbz2-dev libffi-dev

CentOS:

    yum install gcc gcc-c++ unzip git redis curl bzip2-devel

```eval_rst
.. important::
   CentOS: Make sure redis is running before continuing. ::
   
      systemctl enable redis.service
      systemctl start redis.service
```

## Database Setup

Alliance Auth needs a MySQL user account and database. Open an SQL shell with `mysql -u root -p` and create them as follows, replacing `PASSWORD` with an actual secure password:

    CREATE USER 'allianceserver'@'localhost' IDENTIFIED BY 'PASSWORD';
    CREATE DATABASE alliance_auth;
    GRANT ALL PRIVILEGES ON alliance_auth . * TO 'allianceserver'@'localhost';

Close the SQL shell and secure your database server with the `mysql_secure_installation` command.

## Auth Install

### User Account

For security and permissions, it’s highly recommended you create a separate user to install under.

Ubuntu:

    adduser --disabled-login allianceserver

CentOS:

    useradd -s /bin/nologin allianceserver

### Virtual Environment

Create a Python virtual environment and put it somewhere convenient (e.g. `/home/allianceserver/venv/auth/`)

    python3 -m venv /home/allianceserver/venv/auth/

```eval_rst
.. tip::
   A virtual environment provides support for creating a lightweight "copy" of Python with their own site directories. Each virtual environment has its own Python binary (allowing creation of environments with various Python versions) and can have its own independent set of installed Python packages in its site directories. You can read more about virtual environments on the Python_ docs.
.. _Python: https://docs.python.org/3/library/venv.html
```
    
Activate the virtualenv using `source /home/allianceserver/venv/auth/bin/activate`. Note the `/bin/activate` on the end of the path.

```eval_rst
.. hint::
   Each time you come to do maintenance on your Alliance Auth installation, you should activate your virtual environment first. When finished, deactivate it with the 'deactivate' command.
```

### Alliance Auth Project

You can install the library using `pip install allianceauth`. This will install Alliance Auth and all its python dependencies.

Now you need to create the application that will run the Alliance Auth install. Ensure you are in the allianceserver home directory by issuing `cd /home/allianceserver`.

The `allianceauth start myauth` command will bootstrap a Django project which will run Alliance Auth. You can rename it from `myauth` to anything you'd like: this name is shown by default as the site name but that can be changed later.

```eval_rst
.. tip::
   If you plan to use gunicorn as your WSGI server (recommended), ensure it is installed before starting your auth project to have an entry automatically created in the project's supervisor config file. ::
   
      pip install gunicorn
```

The settings file needs configuring. Edit the template at `myauth/myauth/settings/local.py`. Be sure to configure the EVE SSO and Email settings.

Django needs to install models to the database before it can start.

    python /home/allianceserver/myauth/manage.py migrate

Now we need to round up all the static files required to render templates. Make a directory to serve them from and populate it.
    
    mkdir -p /var/www/myauth/static
    python /home/allianceserver/myauth/manage.py collectstatic
    chown -R www-data:www-data /var/www/myauth/static

Check to ensure your settings are valid.

    python /home/allianceserver/myauth/manage.py check

And finally ensure the allianceserver user has read/write permissions to this directory before proceeding.

    chown -R allianceserver:allianceserver /home/allianceserver/myauth

## Background Tasks

### Gunicorn

To run the auth website a [WSGI Server](https://www.fullstackpython.com/wsgi-servers.html) is required. [Gunicorn](http://gunicorn.org/) is highly recommended for its ease of configuring. Installation is simple: `pip install gunicorn`. It can be manually called with `gunicorn myauth.wsgi` or automatically run using supervisor.

Additional information is available in the [gunicorn](gunicorn.md) doc.

### Supervisor

[Supervisor](http://supervisord.org/) is a process watchdog service: it makes sure other processes are started automatically and kept running. It can be used to automatically start the WSGI server and celery workers for background tasks. Installation varies by OS:

Ubuntu:

    apt-get install supervisor

CentOS:

    yum install supervisor
    systemctl enable supervisord.service
    systemctl start supervisord.service

Once installed it needs a configuration file to know which processes to watch. Your Alliance Auth project comes with a ready-to-use template which will ensure the celery workers, celery task scheduler and gunicorn are all running.

    ln /home/allianceserver/myauth/supervisor.conf /etc/supervisor/conf.d/myauth.conf
    supervisorctl reload

You can check the status of the processes with `supervisorctl status`. Logs from these processes are available in `/home/allianceserver/myauth/log` named by process.

```eval_rst
.. note::
   Any time the code or your settings change you'll need to restart gunicorn and celery. ::
   
       supervisorctl restart myauth:
```

## Webserver

Once installed, decide on whether you're going to use [NGINX](nginx.md) or [Apache](apache.md) and follow the respective guide.

## Superuser

Before using your auth site it is essential to create a superuser account. This account will have all permissions in Alliance Auth. It's OK to use this as your personal auth account.

    python /home/allianceserver/myauth/manage.py createsuperuser

```eval_rst
.. important::
   Be sure to add a main character to this account before attempting to activate services with it.
```

## Updating

Periodically [new releases](https://github.com/allianceauth/allianceauth/releases/) are issued with bug fixes and new features. To update your install, simply activate your virtual environment and update with `pip install --upgrade allianceauth`. Be sure to read the release notes which will highlight changes.

Some releases come with changes to settings: update your project's settings with `allianceauth update /home/allianceserver/myauth`.

Some releases come with new or changed models. Update your database to reflect this with `python /home/allianceserver/myauth/manage.py migrate`.
 
Always restart celery and gunicorn after updating.