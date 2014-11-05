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

export MYSQL_ROOT_PASS=poitot

sudo debconf-set-selections <<< "mysql-server mysql-server/root_password password $MYSQL_ROOT_PASS"
sudo debconf-set-selections <<< "mysql-server mysql-server/root_password_again password $MYSQL_ROOT_PASS"
sudo apt-get -y install mysql-server-5.5

#check it's up
sudo mysqladmin status -p$MYSQL_ROOT_PASS

echo 'Creating databases and allianceauth user'
sudo mysqladmin -p$MYSQL_ROOT_PASS create alliance_auth 
sudo mysqladmin -p$MYSQL_ROOT_PASS create alliance_forum
sudo mysqladmin -p$MYSQL_ROOT_PASS create alliance_mumble

sudo mysql -u root -p$MYSQL_ROOT_PASS -e "CREATE USER 'allianceauth'@'localhost' IDENTIFIED BY 'allianceauth'"
sudo mysql -u root -p$MYSQL_ROOT_PASS -e "GRANT ALL PRIVILEGES ON * . * TO 'allianceauth'@'localhost'";

sudo mysqladmin -p$MYSQL_ROOT_PASS flush-privileges

sudo apt-get -y install rabbitmq-server

sudo pip install -r requirements.txt

chmod +x *.sh

echo '--------'
echo 'Almost there!'
echo 'Next steps:\n'
echo '1. Adjust mysql root password if you feel so inclined.'
echo '2. Adjust all the stuff in ./alliance_auth/settings.py.'
echo '3. Comment out bootstrap_permissions() inside groupmanagement/__init__.py'
echo '4. Run sudo python manage.py syncdb to set up the database tables'
echo '5. Uncomment that line that you commented out in step 3.'
echo "6. run cd /vagrant/; ./startup.sh to start, and ./shutdown.sh to stop."
echo '--------'
