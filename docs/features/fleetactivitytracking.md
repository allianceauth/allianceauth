# Fleet Activity Tracking

## Installation

Fleet Activity Tracking requires access to the `esi-location.read_location.v1`, `esi-location.read_ship_type.v1`, and `esi-universe.read_structures.v1` SSO scopes. Update your application on the [EVE Developers site](https://developers.eveonline.com) to ensure these are available.

Add `'allianceauth.fleetactivitytracking',` to your `INSTALLED_APPS` list in your auth project's settings file. Run migrations to complete installation.