#!/usr/bin/env bash
python manage.py syncdb

python manage.py shell < run_alliance_corp_update.py

python manage.py celeryd --verbosity=2 --loglevel=DEBUG
python manage.py celerybeat --verbosity=2 --loglevel=DEBUG
python manage.py runserver
