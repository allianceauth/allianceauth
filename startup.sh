#!/usr/bin/env bash
python manage.py syncdb

python manage.py shell
    from util import bootstrap_permissions
    from celerytask.tasks import run_alliance_corp_update
    bootstrap_permissions()
    run_alliance_corp_update()

python manage.py celeryd --verbosity=2 --loglevel=DEBUG
python manage.py celerybeat --verbosity=2 --loglevel=DEBUG
python manage.py runserver
