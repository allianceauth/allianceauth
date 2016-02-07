pip install -r requirements.txt
yes yes | python manage.py syncdb
yes yes | python manage.py evolve --hint --execute
yes yes | python manage.py collectstatic
