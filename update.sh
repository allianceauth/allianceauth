pip install -r requirements.txt
python manage.py migrate
yes yes | python manage.py collectstatic
python manage.py shell < run_alliance_corp_update.py
