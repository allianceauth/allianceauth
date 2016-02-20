pip install --upgrade -r requirements.txt
yes yes | python manage.py syncdb
yes yes | python manage.py evolve --hint --execute
yes yes | python manage.py collectstatic
python manage.py shell < run_alliance_corp_update.py
