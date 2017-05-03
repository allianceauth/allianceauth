# Quick Start

Once you’ve installed AllianceAuth, perform these steps to get yourself up and running.

First you need a superuser account. You can use this as a personal account. From the command line, `python manage.py createsuperuser` and follow the prompts.

The big goal of AllianceAuth is the automation of group membership, so we’ll need some groups. In the admin interface, select `Groups`, then at the top-right select `Add Group`. Give it a name and select permissions. Special characters (including spaces) are removing before syncing to services, so try not to have group names which will be the same upon cleaning. A description of permissions can be found in the [readme file](https://github.com/allianceauth/allianceauth/blob/master/README.md). Repeat for all the groups you see fit, whenever you need a new one.

### Background Processes

To start the background processes to sync groups and check api keys, issue these commands:

    screen -dm bash -c 'celery -A alliance_auth worker'
    screen -dm bash -c 'celery -A alliance_auth beat'
