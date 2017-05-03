# Supervisor

>Supervisor is a client/server system that allows its users to control a number of processes on UNIX-like operating systems.

What that means is supervisor will take care of ensuring the celery workers are running (and mumble authenticator) and start the automatically on reboot. Handy, eh?

## Installation

Most OSes have a supervisor package available in their distribution.

Ubuntu:

    sudo apt-get install supervisor

CentOS:

    sudo yum install supervisor
    sudo systemctl enable supervisor.service
    sudo systemctl start supervisor.service

## Configuration

Auth provides example config files for the celery workers, the periodic task scheduler (celery beat), and the mumble authenticator. All of these are available in `thirdparty/Supervisor`.

For most users, all you have to do is copy the config files to `/etc/supervisor/conf.d` then restart the service. Copy `auth-celerybeat.conf` and `auth-celeryd.conf` for the celery workers, and `auth-mumble.conf` for the mumble authenticator. For all three just use a wildcard:

    sudo cp thirdparty/Supervisor/* /etc/supervisor/conf.d

Ubuntu:

    sudo service supervisor restart

CentOS:

    sudo systemctl restart supervisor.service

## Checking Status

To ensure the processes are working, check their status:

    sudo supervisorctl status

Processes will be `STARTING`, `RUNNING`, or `ERROR`. If an error has occurred, check their log files:
 - celery workers: `log/worker.log`
 - celery beat: `log/beat.log`
 - authenticator: `log/authenticator.log`

## Customizing Config Files

The only real customization needed is if running in a virtual environment. The python path will have to be changed in order to start in the venv.

Edit the config files and find the line saying `command`. Replace `python` with `/path/to/venv/bin/python`. For Celery replace `celery` with `/path/to/venv/bin/celery`. This can be relative to the `directory` specified in the config file.

Note that for config changes to be loaded, the supervisor service must be restarted.

## Troubleshooting

### auth-celerybeat fails to start
Most often this is caused by a permissions issue on the allianceauth directory (the error will talk about `celerybeat.pid`). The easiest fix is to edit its config file and change the `user` from `allianceserver` to `root`.

### Workers are using old settings

Every time the codebase is updated or settings file changed, workers will have to be restarted. Easiest way is to restart the supervisor service (see configuration above for commands)