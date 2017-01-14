# Dependencies

## Ubuntu

Tested on Ubuntu 12, 14, 15, and 16. Package names and repositories may vary.

### Core
Required for base auth site

#### Python

    python python-dev python-mysqldb python-setuptools python-mysql.connector python-pip

#### MySQL

    mysql-server mysql-client libmysqlclient-dev

#### Utilities

    screen unzip git redis-server curl libssl-dev libbz2-dev libffi-dev

### Apache
Required for displaying web content

    apache2 libapache2-mod-php5 libapache2-mod-wsgi

### PHP
Required for phpBB, smf, evernus alliance market, etc

    php5 php5-gd php5-mysqlnd php5-curl php5-gd php5-intl php-pear php5-imagick php5-imap php5-mcrypt php5-memcache php5-ming php5-ps php5-pspell php5-recode php5-snmp php5-sqlite php5-tidy php5-xmlrpc php5-xsl

### Java
Required for hosting jabber server

    oracle-java8-installer

## CentOS 7

### Add The EPEL Repository

    yum --enablerepo=extras install epel-release
    yum update

### Core
Required for base auth site

#### Python

    python python-devel MySQL-python python-setuptools  mysql-connector-python python-pip bzip2-devel

#### MySQL

    mariadb-server mariadb-devel mariadb

#### Utilities

    screen gcc gcc-c++ unzip git redis curl nano

### Apache
Required for displaying web content

    httpd mod_wsgi

### PHP
Required for phpBB, smf, evernus alliance market, etc

    php php-gd php-mysqlnd php-intl php-pear ImageMagick php-imap php-mcrypt php-memcache php-pspell php-recode php-snmp php-pdo php-tidy php-xmlrpc

### Java
Required for hosting jabber server

    java libstdc++.i686
