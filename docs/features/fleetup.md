# Fleetup

## Installation

Add `allianceauth.fleetup` to your auth project's `INSTALLED_APPS` setting.

    INSTALLED_APPS += ['allianceauth.fleetup']

Additional settings are required. Append the following settings to the end of your auth project's settings file and fill them out.

    FLEETUP_APP_KEY = ''  # The app key from http://fleet-up.com/Api/MyApps
    FLEETUP_USER_ID = ''  # The user id from http://fleet-up.com/Api/MyKeys
    FLEETUP_API_ID = ''  # The API id from http://fleet-up.com/Api/MyKeys
    FLEETUP_GROUP_ID = ''  # The id of the group you want to pull data from, see http://fleet-up.com/Api/Endpoints#groups_mygroupmemberships

Once filled out restart gunicorn and celery.

## Permissions

The Fleetup module is only visible to users with the `auth | user | view_fleeup` permission.