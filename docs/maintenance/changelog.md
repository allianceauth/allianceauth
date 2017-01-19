# Changelog

## From now on all changelogs will be included as release notes.
https://github.com/allianceauth/allianceauth/releases

### 547
Oct 16

Golly this is a big one. Upgrading takes a bit of work. [For full instructions click here.](https://github.com/allianceauth/allianceauth/pull/547#issue-183247630)

 - Update django version to 1.10
 - Remove member/blue permissions
   - implement user states
 - implement Django's messaging framework for site feedback
 - remove pathfinder support
 - remove fleet fits page
 - remove wormhole tracker
 - do not store service passwords
 - supervisor configs for celery tasks and authenticator
 - buttons on admin site to sync service groups
 - show number of notifications
 - fix all button css
 - rewrite and centralize API checks
 - bulk mark read / delete for notifications
 - replace hard-coded urls with reverse by name
 - python 3 compatibility
 - correct navbar active link with translated urls

### 468
June 12
 - XenForo integration added
 - Discord integration updated to use OAuth and official API
 - FleetUp fixes for empty responses

### 441
May 27
 - Added option to require new API keys
   - Reduces threat of stolen keys being used to create accounts
   - Requires two new settings:
     - `REJECT_OLD_APIS`, default `False`
     - `REJECT_OLD_APIS_MARGIN`, default 50

### 423
May 9
 - Added statistics to fleet activity tracking
 - Capture teamspeak error codes in logs from failed account creation

### 401
Apr 29
 - Added FleetUp integration
 - Added Fleet Activity Tracking links
   - settings.py has new entries and will have to be updated

### 394
Apr 17
 - Added Discourse integration
 - Added Pathfinder integration
   - settings.py has new entries and will have to be updated

### 386
Apr 15 2016
 - Corrected Teamspeak group sync triggers
 - Modified username sanitization to reduce username collisions

### 369
Apr 7 2016
 - Added Evernus Alliance Market Integration
   - Requires libffi-devel (centos) or libffi-dev (ubuntu) and pip install bcrypt

### 365
Apr 6 2016
 - Added SMF2 Forums integration
   - Requires a settings.py file update for existing installs

### 360
Apr 4 2016
 - Added a countdown / local time to the fleet operations timers
 - Fixed the corporation structure timers so the countdown shows up correctly

### 340
Mar 31 2016
 - Added Support for IP Board 4 / IP Suite 4
   - You must update settings.py accordingly if updating form a previous version.
   - only allows for the member group to sync. Additional groups must be manually added
 - Fixed a bug with corporation stats not showing correct users and numbers

### 328
Mar 24 2016
 - Added Enhancements to the SRP Management
   - Users can now enable and disable srp links.
   - The Approve and Reject buttons will show up depending on the srp status.
   - Fixed an issue where SRP Requests were not getting the proper status assigned.

### 321
Mar 23 2016
 - Added Ship types and kill board data to the SRP management.
   - These are automatically pulled from zKillboard.
   - zKillboard is the only killboard links that the SRP Manager Accepts Now.

### 314
Mar 22 2016
 - Revamp of the Human Resources Application and Management System
   - see the [docs](../features/hrapplications.md) for how to use the new system
   - a completely untested conversion script exists. If you want to view your old models, contact Adarnof to try it out
 - Moved Error Handling for the API Keys to the API Calls to better handle API server outages
 - Removed the infamous database update task
   - implemented a receiver to update service groups as they change

To remove the database update task from the scheduler, navigate to your django admin site, and delete the run_databaseUpdate model from the periodic tasks. Restart celery.

Mumble now uses an ICE authenticator. This requires an additional dependency. Please install `libbz2-dev` and `libssl-dev` prior to running the update script:

    sudo apt-get install libbz2-dev libssl-dev

Now run the update script.

Old Mumble accounts are incompatible. Users will need to recreate them (sorry). To clear the old ones out:

    python manage.py shell
    from services.tasks import disable_mumble
    disable_mumble()

To set up the authenticator, follow the [Mumble setup guide.](../installation/services/mumble.md)

Optional: you can delete the entire mumble database block in settings.py

### 304
Mar 8 2016
 - Repurposed Signature Tracker for Wormhole Use. Combat sites are a ever changing thing therefore removed.
 - Increased run_databaseUpdate time to 10 minutes to address stability problems for larger alliances.

### 296
Feb 27 2016
 - corrected an issue with populating corp stats for characters with missing api keys
 - moved log files to dedicated folder to allow apache access so it can rotate them
 - merged Corp Stats and Member Tracking apps
   - `corp_stats` and `corputils` permissions have been depreciated
   - assign either of `corp_apis` or `alliance_apis` to get access to Corp Stats app
     - `corp_apis` populates APIs of user's main corp
     - `alliance_apis` populates APIs of user's main alliance

### 289
Feb 25 2016
 - Changed the start time format on the fleet operations board to use the 24 hour format
   - Fixed an issue when updating the fleet operations timers the date time picker would not work.

### 286
Feb 23 2016
- Added ability to remove notifications

### 278
Feb 18 2016
 - notifications for events:
   - api failed validation during refresh
   - group request accepted/rejected
   - corp application accepted/rejected
   - services disabled
 - logging notifications include traceback
 - automatically assign alliance groups of the form "Alliance_NAME"
 - parallel corp model updates via celery broker for performance improvements
 - new functions to clear service info for decommissioning a service

settings.py will need to be updated to include the new settings.

### 265
Feb 13 2016
 - prototype notification system
 - logging errors as notifications based on new permission `logging_notifications`

The logging configuration in settings.py has changed. Please update.

### 263
Feb 12 2016
 - revamped `run_corp_update` function which actually works
 - fixed group syncing in discord and openfire

### 259
Feb 11 2016
  - Added ability to edit structure timers
  - Added ability to edit fleet operations timers
  - Added ability to edit Signatures


### 245
Feb 7 2016

 - ability to toggle assigning corp groups
 - users able to manually trigger api refresh

Two new settings in [settings.py](../installation/auth/settings.md) - `MEMBER_CORP_GROUPS` and `BLUE_CORP_GROUPS` - be sure to add them.

### 226
Jan 31 2016

Been a while since one of these was written so a big list.

 - corrected user permission caching for Phpbb3
 - open groups which don't require application approval
 - additional weblink data for TS3 to encourage proper usernames
 - corp-restricted timers
 - signature tracker
 - tolerate random 221 errors from EVE api servers till CCP FoxFour gets it sorted
 - new corp member auditing app
 - fleet operation timers
 - revamped member status checking and assignment

Loads of new permissions. See the readme for descriptions.

Need to install new requirements - `sudo pip install -r requirements.txt`

Incompatible with Python2.6 or older. Please update. Please. It's 2016 people.

Settings.py got nuked. Backup your current settings.py, copy the example, and repopulate.

New caching directory for requests - if you're using apache to serve the site, `cache/` needs to be writable by the webserver. Easiest way is to `chown -R www-data:www-data cache` from within the allianceauth install dir.

### 145
Jan 6 2016

 - complete logging system for all apps
 - custom service passwords
 - Discord token caching to prevent locking out users
 - Jabber broadcast group restrictions
 - Password reset email contains domain
 - Index page only renders forums/killboard/media if url specified
 - timestamps on hrapplication comments
 - corrected corp/alliance model creation logic
 - corrected typecasting of access masks during api checks
 - prevent TS3 from attempting to sync groups if not installed

New permissions - see readme.

Need to install new requirements.

Settings.py has changed. Make a new one from the example.

### 118
Dec 2 2015

 - add timers by time remaining
 - Discord support
 - corrected celerytask logic
 - handle many 500s thrown in views

New settings.py again. Need to reinstall requirements.

### 107
Nov 28 2015

 - added broadcast plugin support for openfire
 - timer addition by remaining time, not fixed date
 - corrected alliance model deletion logic
 - corrected name rendering on templates

Openfire setup guide has been updated for the new plugin.

### 102
Nov 25 2015

 - variable API requirements
 - api access mask validation during refresh
 - support for customization of templates
 - celery task resource reduction
 - vagrant support

All templates and staticfiles have been moved. If you've customized any of these, make a backup before pulling changes.

New command `python manage.py collectstatic` added to install guide. Should be run after every update.

New settings.py template. Make a backup of the old one, copy the example, and populate.

### 87
Nov 15 2015

A couple quality-of-life improvements.

 - corrected an error in the Teamspeak3 Manager improperly parsing responses
 - added the ability to hide groups from the web interface
 - added a feature for phpbb avatars to be set to the character portrait

New permissions for the `HiddenGroup` model only affect the admin site (default model permissions)

The Phpbb3 setup guide has been updated to reflect avatars.

### 72
Nov 5th 2015

On November 5th we performed two major pulls from Adarnof’s and Kaezon’s forks.

Improvements include:

 - ability to deploy for either corp or alliance
 - improved logic for member status transitions
 - group syncing to TS3
 - template corrections

Migration to the new version is a bit trickier because of changes to settings.py - it's easiest to archive the old one, make a copy of the new template, and repopulate it.
