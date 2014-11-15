Alliance Auth
============

Alliance service auth to help large scale alliances manage services.
Built for "The 99 Percent" open for anyone to use

[Project Website](http://r4stl1n.github.io/allianceauth/)

[Dev Setup Guide] (http://r4stl1n.github.io/allianceauth/quicksetup.html)

[Production Setup Guide] (http://r4stl1n.github.io/allianceauth/fullsetup.html)

Requirements:

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
	rabbitmq server
        
Startup Instructions:

    ./bootstrap.sh (Sudo if needed)
    ./startup.sh
    ./shutdown.sh
    

Special Permissions In Admin:

    auth | user | alliance_member ( Added auto by auth when a member is verified )
    auth | user | group_management ( Access to add members to groups within the alliance )
    auth | user | human_resources ( Corp only access to view applications )
    auth | user | jabber_broadcast ( Access to broadcast a message over jabber to specific groups or all)
    auth | user | blue_memeber ( Auto Added to people who register has a blue when adding api key)
    auth | user | corp_stats (View basic corp auth stats *who is authed etc*)
