# Troubleshooting

## Something broken? Stuck on an issue? Can't get it set up?

Start by checking the [issues](https://github.com/allianceauth/allianceauth/issues?utf8=%E2%9C%93&q=is%3Aissue) - especially closed ones.

No answer?
 - open an [issue](https://github.com/allianceauth/allianceauth/issues)
 - harass us on [gitter](https://gitter.im/R4stl1n/allianceauth)

## Common Problems

### `pip install -r requirements.txt` is failing

It's probably a permissions issue. Ensure your current user can write to the virtual environment folder. That, or you're missing a dependency of some kind which will be indicated in the error message.

### I'm getting an error 500 trying to connect to the website on a new install

*Great.* Error 500 is the generic message given by your web server when *anything* breaks. The actual error message is hidden in one of your auth project's log files. Read them to identify it.

### Failed to configure log handler

Make sure the log directory is writeable by the allianceserver user: `chmown -R allianceserver:allianceserver /path/to/myauth/log/`, then restart the auth supervisor processes.

### Groups aren't syncing to services

Make sure the background processes are running: `supervisorctl status myauth:`. If `myauth:worker` or `myauth:beat` do not show `RUNNING` read their log files to identify why.

### Task queue is way too large

Stop celery workers with `supervisorctl stop myauth:worker` then clear the queue:

    redis-cli FLUSHALL
    celery -A myauth worker --purge

Press Control+C once.

Now start the worker again with `supervisorctl start myauth:worker`

### Proxy timeout when entering email address

This usually indicates an issue with your email settings. Ensure these are correct and your email server/service is properly configured.

### No images are available to users accessing the website

This is due to a permissions mismatch, check the setup guide for your web server. Additionally ensure the user who owns /var/www/myauth/static is the same user as running your webserver, as this can be non-standard.

### Unable to execute 'gunicorn myauth.wsgi' or ImportError: No module named 'myauth.wsgi'

Gunicorn needs to have context for its running location, `/home/alllianceserver/myauth/gunicorn myauth.wsgi` will not work, instead `cd /home/alllianceserver/myauth` then `gunicorn myauth.wsgi` is needed to boot Gunicorn. This is handled in the Supervisor config, but this may be encountered running Gunicorn manually for testing.
