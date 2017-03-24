pip install --upgrade -r requirements.txt
python manage.py migrate --fake-initial
yes yes | python manage.py collectstatic -c
python manage.py check --deploy