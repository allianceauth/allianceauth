Alliance Auth
============

[![Join the chat at https://gitter.im/R4stl1n/allianceauth](https://badges.gitter.im/R4stl1n/allianceauth.svg)](https://gitter.im/R4stl1n/allianceauth?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Alliance service auth to help large scale alliances manage services.
Built for "The 99 Percent" open for anyone to use

[Documentation and Setup Guides](https://github.com/R4stl1n/allianceauth/wiki)

[Project Website](http://r4stl1n.github.io/allianceauth/)

[Old Dev Setup Guide] (http://r4stl1n.github.io/allianceauth/quicksetup.html)

[Old Production Setup Guide] (http://r4stl1n.github.io/allianceauth/fullsetup.html)

Join us in-game in the channel allianceauth for help and feature requests.

Special Thanks: 

    Thanks to Nikdoof, without his old auth implementation this project wouldn't be as far as it is now.

Note:

    Please keep your admin account and normal accounts separate. If you are the admin only use 
    the admin account for admin stuff do not attempt to use it for your personal services. 
    Create a new normal account for this or things will break.
    
Requirements:

    # Django Stuff #
    django 1.10.1
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
    
    # Needed Apps #
    Rabbitmq server
        
Startup Instructions:

    ./bootstrap.sh (Sudo if needed)
    ./startup.sh
    ./shutdown.sh

Vagrant Instructions:

    Copy the scripts to the root directory before running

Special Permissions In Admin:

    auth | user | group_management ( Access to add members to groups within the alliance )
    auth | user | jabber_broadcast ( Access to broadcast a message over jabber to own groups)
    auth | user | jabber_broadcast_all ( Can choose from all groups and the 'all' option when broadcasting)
    auth | user | corp_apis ( View APIs, and jackKnife, of all members in user's corp. )
    auth | user | alliance_apis ( View APIs, and jackKnife, of all member in user's alliance member corps. )
    auth | user | timer_management ( Access to create and remove timers)
    auth | user | timer_view ( Access to timerboard to view timers)
    auth | user | srp_management ( Allows for an individual to create and remove srp fleets and fleet data)
    auth | user | sigtracker_management ( Allows for an individual to create and remove signitures)
    auth | user | sigtracker_view ( Allows for an individual view signitures)
    auth | user | optimer_management ( Allows for an individual to create and remove fleet operations)
    auth | user | optimer_view ( Allows for an individual view fleet operations)
    auth | user | logging_notifications ( Generate notifications from logging)

    auth | user | human_resources ( View applications to user's corp )
    hrapplications | application | delete_application ( Can delete applications )
    hrapplications | application | accept_application ( Can accept applications )
    hrapplications | application | reject_application ( Can reject applications )
    hrapplications | application | view_apis ( Can see applicant's API keys )
    hrapplications | applicationcomment | add_applicationcomment ( Can comment on applications )

Active Developers

    Adarnof
    Kaezon Rio
    Mr McClain

Beta Testers/ Bug Fixers:

    TrentBartlem ( Testing and Bug Fixes)
    IskFiend ( Bug Fixes and Server Configuration )
    Mr McClain (Bug Fixes and server configuration)
