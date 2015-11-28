#!/usr/bin/env bash

# TODO route log output to file.
yes yes | python manage.py collectstatic
python manage.py syncdb
yes yes | python manage.py evolve --hint --execute

python manage.py shell < run_alliance_corp_update.py

python manage.py celeryd --verbosity=2 --loglevel=DEBUG &
python manage.py celerybeat --verbosity=2 --loglevel=DEBUG &

python manage.py runserver &
