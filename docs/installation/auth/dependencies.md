# Dependencies

## Ubuntu

Tested on Ubuntu 14.04LTS, 16.04LTS and 17.04. Package names and repositories may vary. Please note that 14.04LTS comes with Python 3.4 which may be insufficient.

### Core
Required for base auth site

#### Python

    python3 python3-dev python3-setuptools python3-pip

#### MySQL

    mariadb-server mysql-client libmysqlclient-dev

#### Utilities

    unzip git redis-server curl libssl-dev libbz2-dev libffi-dev

## CentOS 7

Tested on CentOS 7

### Add The IUS Repository

    sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    yum update

### Core
Required for base auth site

#### Python

    python36u python36u-devel python36u-setuptools python36u-pip bzip2-devel

#### MySQL

    mariadb-server mariadb-devel mariadb

#### Utilities

    gcc gcc-c++ unzip git redis curl nano
