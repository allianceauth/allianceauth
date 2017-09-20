# -*- coding: utf-8 -*-
from setuptools import setup
import allianceauth


setup(
    name='allianceauth',
    version=allianceauth.__version__,
    author='Alliance Auth',
    author_email='adarnof@gmail.com',
    description='Eve alliance auth for the 99 percent',
    # Any changes in these package requirements
    # should be reflected in requirements.txt as well.
    install_requires=[
        'mysqlclient',
        'dnspython',
        'passlib',
        'requests>=2.9.1',
        'bcrypt',
        'python-slugify>=1.2',
        'requests-oauthlib',

        'redis',
        'celery>=4.0.2',

        'django>=1.10,<2.0',
        'django-bootstrap-form',
        'django-bootstrap-pagination',
        'django-registration',
        'django-sortedm2m',
        'django-redis-cache>=1.7.1',
        'django-celery-beat',

        # Openfire
        'openfire-restapi',
        'sleekxmpp',

        'adarnauth-esi>=1.4,<2.0',
    ],
    license='GPLv2',
    packages=['allianceauth'],
    url='https://github.com/allianceauth/allianceauth',
    zip_safe=False,
    include_package_data=True,
)
