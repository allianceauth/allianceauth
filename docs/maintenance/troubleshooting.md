# Troubleshooting

## Something broken? Stuck on an issue? Can't get it set up?

Start here:
 - check the [issues](https://github.com/allianceauth/allianceauth/issues?utf8=%E2%9C%93&q=is%3Aissue) - especially closed ones
 - check the [forums](https://forums.eveonline.com/default.aspx?g=posts&t=383030)

No answer?
 - open an [issue](https://github.com/allianceauth/allianceauth/issues)
 - harass us on [gitter](https://gitter.im/R4stl1n/allianceauth)
 - post to the [forums](https://forums.eveonline.com/default.aspx?g=posts&t=383030)

## Common Problems

### `pip install -r requirements.txt` is failing

Either you need to `sudo` that command, or it's a missing dependency. Check [the list](../installation/auth/dependencies.md), reinstall, and try again.

### I'm getting an error 500 trying to connect to the website on a new install

Read the apache error log: `sudo nano /var/log/apache2/error.log`

If it talks about failing to import something, google its name and install it.

If it whines about being unable to configure logger, see below. 

### Failed to configure log handler

Make sure the log directory is write-able: `chmod -R 777 /home/allianceserver/allianceauth/log`, then reload apache/celery/supervisor/etc.

### Groups aren't syncing to services

Make sure the background processes are running: `ps aux | grep celery` should return more than 1 line. More lines if you have more cores on your server's processor. If there are more than two lines starting with `SCREEN`, kill all of them with `kill #` where `#` is the process ID (second column), then restart with [these background process commands](../installation/auth/quickstart.md) from the allianceauth directory. You can't start these commands as root.

If that doesn't do it, try clearing the worker queue. First kill all celery processes as described above, then do the following:

    redis-cli FLUSHALL
    python manage.py celeryd --purge

Press control+C once.

    python manage.py celeryd --discard

Press control+C once.

Now start celery again with [these background process commands.](../installation/auth/quickstart.md)

While debugging, it is useful to see if tasks are being executed. The easiest tool is [flower](http://flower.readthedocs.io/). Install it with this: `sudo pip install flower`, then start it with this: `celery flower --broker=amqp://guest:guest@localhost:5672//`. To view the status, navigate to your server IP, port 5555.
