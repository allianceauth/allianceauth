Alliance Auth
============

[![Join the chat at https://gitter.im/R4stl1n/allianceauth](https://badges.gitter.im/R4stl1n/allianceauth.svg)](https://gitter.im/R4stl1n/allianceauth?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Documentation Status](https://readthedocs.org/projects/allianceauth/badge/?version=latest)](http://allianceauth.readthedocs.io/?badge=latest)
[![Build Status](https://travis-ci.org/allianceauth/allianceauth.svg?branch=master)](https://travis-ci.org/allianceauth/allianceauth)
[![Coverage Status](https://coveralls.io/repos/github/allianceauth/allianceauth/badge.svg?branch=master)](https://coveralls.io/github/allianceauth/allianceauth?branch=master)


EVE service auth to help corps, alliances, and coalitions manage services.
Built for "The 99 Percent" open for anyone to use.

[Read the docs here.](http://allianceauth.rtfd.io)

Special Permissions In Admin:

    auth | user | group_management ( Access to add members to groups within the alliance )
    auth | user | jabber_broadcast ( Access to broadcast a message over jabber to own groups )
    auth | user | jabber_broadcast_all ( Can choose from all groups and the 'all' option when broadcasting )
    auth | user | corp_apis ( View APIs, and jackKnife, of all members in user's corp. )
    auth | user | alliance_apis ( View APIs, and jackKnife, of all member in user's alliance member corps. )
    auth | user | timer_management ( Access to create and remove timers )
    auth | user | timer_view ( Access to timerboard to view timers )
    auth | user | srp_management ( Allows for an individual to create and remove srp fleets and fleet data )
    auth | user | sigtracker_management ( Allows for an individual to create and remove signitures )
    auth | user | sigtracker_view ( Allows for an individual view signitures )
    auth | user | optimer_management ( Allows for an individual to create and remove fleet operations )
    auth | user | optimer_view ( Allows for an individual view fleet operations )
    auth | user | logging_notifications ( Generate notifications from logging )

    auth | user | human_resources ( View applications to user's corp )
    hrapplications | application | delete_application ( Can delete applications )
    hrapplications | application | accept_application ( Can accept applications )
    hrapplications | application | reject_application ( Can reject applications )
    hrapplications | application | view_apis ( Can see applicant's API keys )
    hrapplications | applicationcomment | add_applicationcomment ( Can comment on applications )

Vagrant Instructions:

    Copy the scripts to the root directory before running

Active Developers:

    Adarnof
    basraah

Beta Testers/ Bug Fixers:

    TrentBartlem ( Testing and Bug Fixes )
    IskFiend ( Bug Fixes and Server Configuration )
    Mr McClain (Bug Fixes and server configuration )

Special Thanks:

    Thanks to Nikdoof, without his old auth implementation this project wouldn't be as far as it is now.
