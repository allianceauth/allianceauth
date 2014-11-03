#!/usr/bin/env bash

sudo apt-get update

sudo apt-get clean

sudo apt-get -y install libtool
sudo apt-get -y install python-dev libyaml-dev libffi-dev
sudo apt-get -y install python-pip

cd /vagrant/

sudo pip install --upgrade pip

# Pip moved location after upgrade from 1.0
sudo ln -s /usr/local/bin/pip /usr/bin/pip 2>/dev/null

sudo apt-get -y install libmysqlclient-dev 

sudo pip install --allow-external mysql-connector-python mysql-connector-python
sudo pip install --allow-external python-openfire python-openfire==0.2.3-beta
sudo pip install https://github.com/eve-val/evelink/zipball/master
sudo pip install --allow-external libffi-dev libffi-dev

#TODO collect user input and use that to populate the passwords
sudo apt-get -y install mysql-server-5.5
sudo apt-get -y install rabbitmq-server
#sudo apt-get -y install python-xmpp 

sudo pip install -r requirements.txt

chmod +x startup.sh

echo '--------'
echo 'This would be a good point to adjust mysql passwords, as well as all the stuff '
echo 'in ./alliance_auth/settings.py otherwise startup.sh will not work.'
echo '--------'