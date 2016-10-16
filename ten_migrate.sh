pip install -r requirements.txt
python manage.py migrate --fake admin 0001_initial
python manage.py migrate --fake djcelery 0001_initial
python manage.py migrate --fake sessions 0001_initial
python manage.py migrate --fake auth 0001_initial
python manage.py migrate admin
python manage.py migrate sessions
python manage.py migrate djcelery
python manage.py migrate auth
python manage.py migrate --fake authentication 0001_initial
python manage.py migrate --fake celerytask 0001_initial
python manage.py migrate --fake eveonline 0001_initial
python manage.py migrate --fake fleetactivitytracking 0001_initial
python manage.py migrate --fake groupmanagement 0001_initial
python manage.py migrate --fake hrapplications 0001_initial
python manage.py migrate --fake notifications 0001_initial
python manage.py migrate --fake optimer 0001_initial
python manage.py migrate --fake services 0001_initial
python manage.py migrate --fake sigtracker 0001_initial
python manage.py migrate --fake srp 0001_initial
python manage.py migrate --fake timerboard 0001_initial
python manage.py migrate
mysql -u root -p -e 'use alliance_auth; drop table sigtracker_sigtracker; drop table celerytask_syncgroupcache;'
