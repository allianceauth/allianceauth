#!/usr/bin/env bash

sudo apt-get update

sudo apt-get clean

sudo apt-get -y install libtool
sudo apt-get -y install python-dev libyaml-dev libffi-dev
sudo apt-get -y install python-pip

cd /vagrant/

sudo pip install --upgrade pip
sudo ln -s /usr/local/bin/pip /usr/bin/pip 2>/dev/null

sudo apt-get -y install libmysqlclient-dev 

sudo pip install --allow-external mysql-connector-python mysql-connector-python
sudo pip install --allow-external python-openfire python-openfire==0.2.3-beta
sudo pip install https://github.com/eve-val/evelink/zipball/master
sudo pip install --allow-external libffi-dev libffi-dev

#TODO collect user input and use that to populate the passwords
sudo apt-get -y install mysql-server-5.5
sudo apt-get -y install rabbitmq-server
sudo apt-get -y install python-xmpp 

sudo pip install -r requirements.txt


# TODO Extract the rest of this file to separate shell script



## comment out bootstrap_permissions() before sync, as per instructions
#cp groupmanagement/__init__.py groupmanagement/__init__.py.bak
#sed "s/bootstrap_permissions()/#bootstrap_permissions()/" groupmanagement/__init__.py.bak > groupmanagement/__init__.py
#python manage.py syncdb
#mv groupmanagement/__init__.py.bak groupmanagement/__init__.py

#python manage.py celeryd --verbosity=2 --loglevel=DEBUG
#python manage.py celerybeat --verbosity=2 --loglevel=DEBUG
#python manage.py runserver