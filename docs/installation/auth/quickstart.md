# Quick Start

Once you’ve installed AllianceAuth, perform these steps to get yourself up and running.

First you need a superuser account. You can use this as a personal account. From the command line, `python manage.py createsuperuser` and follow the prompts.

The big goal of AllianceAuth is the automation of group membership, so we’ll need some groups. In the admin interface, select `Groups`, then at the top-right select `Add Group`. Give it a name and select permissions. Special characters (including spaces) are removing before syncing to services, so try not to have group names which will be the same upon cleaning. Repeat for all the groups you see fit, whenever you need a new one. Check the [groups documentation](../../features/groups.md) for more details on group configuration.

### Background Processes

To start the background processes you should utilise [supervisor](supervisor.md). Previously screen was suggested to keep these tasks running, however this is no longer the preferred method.
