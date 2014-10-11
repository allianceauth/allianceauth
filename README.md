allianceauth
============
Alliance service auth to help large scale alliances manage services.
Built for "The 99 Percent" open for anyone to use

Requirments:

    # Django Stuff #
    django 1.6.1
    django-evolution
    django-bootstrap-form
    django-celery
    
    # Python Stuff #
    python-mysql-connector
    python-mysqld
    python-passlib
    python-evelink
    python-openfire
    
    # Needed Apps
    rabbitmq
    bcrypt
    
Services Interaction:

    # Supported services #
    Phpbb3   (Forums)
    Mumble   (Voice)
    Openfire (Jabber)
    
    
Startup Instructions:

    python manage.py celeryd --verbosity=2 --loglevel=DEBUG
    python manage.py celerybeat --verbosity=2 --loglevel=DEBUG
    python manage.py runserver

    

Eve alliance auth for the 99 percent
