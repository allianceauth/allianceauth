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
    python-xmpp
    python-dnspython
    
    # Needed Apps
    rabbitmq
    bcrypt
    
Services Interaction:

    # Supported services #
    Phpbb3   (Forums)
    Mumble   (Voice)
    Openfire (Jabber)
    
    
Startup Instructions:

    python syncdb
    python manage.py celeryd --verbosity=2 --loglevel=DEBUG
    python manage.py celerybeat --verbosity=2 --loglevel=DEBUG
    python manage.py runserver

Special Permissions In Admin:
    auth | user | alliance_member ( Added auto by auth when a member is verified )
    auth | user | group_management ( Access to add members to groups within the alliance )
    auth | user | human_resources ( Corp only access to view applications )
    auth | user | jabber_broadcast ( Access to broadcast a message over jabber to specific groups or all)


Note:

    In order to create permissions automatically you there is a "bootstrap_permissions" function in the
    __init__.py of the groupmanagement folder. Comment out before running syncdb, after add it back.
    This is there because i currently have no idea how to do this any other way.

    

Eve alliance auth for the 99 percent
