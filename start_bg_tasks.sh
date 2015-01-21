#!/bin/bash
cd ${0%/*}
screen -dm bash -c 'python manage.py celeryd --verbosity=2 --loglevel=DEBUG'
screen -dm bash -c 'python manage.py celerybeat --verbosity=2 --loglevel=DEBUG'
