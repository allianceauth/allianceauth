pip install --upgrade -r requirements.txt
python manage.py migrate --fake-initial
yes yes | python manage.py collectstatic
python manage.py shell < run_alliance_corp_update.py
