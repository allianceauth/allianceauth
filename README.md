Alliance Auth
============

Alliance service auth to help large scale alliances manage services.
Built for "The 99 Percent" open for anyone to use

[Project Website](http://r4stl1n.github.io/allianceauth/)

[Dev Setup Guide] (http://r4stl1n.github.io/allianceauth/quicksetup.html)

[Production Setup Guide] (http://r4stl1n.github.io/allianceauth/fullsetup.html)

Special Thanks: 

    Thanking [Nikdoof](https://github.com/nikdoof), without his old auth 
    implementation this project wouldn't be as far as it is now.

Note:

    Please keep your admin account and normal accounts separate. If you are the admin only use 
    the admin account for admin stuff do not attempt to use it for your personal services. 
    Create a new normal account for this or things will break.
    
Update Note:
    
    The recent HRApplication update broke evolve somehow.. Im sure its in the way i 
    redid the models. To update when you get the evolve error is first. We need to 
    remove the old hr tables from mysql. We then need to wipe the evolve records in 
    the admin section of the auth. Also keep in mind that modifying the mysql database 
    is dangerous and could corrupt the database if mistakes are made.
    
    python manage.py syncdb
    python manage.py evolve --hint --execute
    
    To wipe the mysql databse execute the following:
        mysql -u MYSQLUSER -p
        use ALLIANCEAUTHDATABASE;
        drop table hrapplications_hrapplication;
        drop table hrapplications_hrapplicationcomment;
        
    Now go back to the admin interface in both of the evolve sections delete all the entries.
    After that go to your shell and run the following.
        python manage.py syncdb;
        python manage.py shell;
              from util import bootstrap_permissions
              bootstrap_permissions()
              exit()
    
    This next step is only needed if you hadn't updated since teh IPBoard update.
    Back to mysql database and execute the following:
        mysql -u MYSQLUSER -p
        use ALLIANCEAUTHDATBASE;
        ALTER TABLE authentication_authservicesinfo ADD ipboard_password  VARCHAR(254);
        ALTER TABLE authentication_authservicesinfo ADD ipboard_username  VARCHAR(254);
        
    Now restart mysql and httpd
        sudo /etc/init.d/mysqld restart
        sudo /etc/init.d/apache2 restart
    
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
	Rabbitmq server
        
Startup Instructions:

    ./bootstrap.sh (Sudo if needed)
    ./startup.sh
    ./shutdown.sh

Vagrant Instructions:

    Copy the scripts to the root directory before running

Special Permissions In Admin:

    auth | user | alliance_member ( Added auto by auth when a member is verified )
    auth | user | group_management ( Access to add members to groups within the alliance )
    auth | user | human_resources ( Corp only access to view applications )
    auth | user | jabber_broadcast ( Access to broadcast a message over jabber to specific groups or all)
    auth | user | blue_member ( Auto Added to people who register has a blue when adding api key)
    auth | user | corp_stats (View basic corp auth stats *who is authed etc*)
    auth | user | timer_management ( Access to create and remove timers)


Beta Testers/ Bug Fixers:

     IskFiend ( Bug Fixes and Server Configuration )
     Mr McClain (Bug Fixes and server configuration)