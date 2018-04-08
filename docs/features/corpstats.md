# Corp Stats

This module is used to check the registration status of corp members and to determine character relationships, being mains or alts.

## Installation

Corp Stats requires access to the `esi-corporations.read_corporation_membership.v1` SSO scope. Update your application on the [EVE Developers site](https://developers.eveonline.com) to ensure it is available.

Add `'allianceauth.corputils',` to your `INSTALLED_APPS` list in your auth project's settings file. Run migrations to complete installation.

## Creating a Corp Stats

Upon initial install, nothing will be visible. For every corp, a model will have to be created before data can be viewed.

![nothing is visible](/_static/images/features/corpstats/blank_header.png)

If you are a superuser, the add button will be immediate visible to you. If not, your user account requires the `add_corpstats` permission.

Corp Stats requires an EVE SSO token to access data from the EVE Swagger Interface. Upon pressing the Add button, you will be prompted to authenticated. Please select the character who is in the corp you want data for.

![authorize from the EVE site](/_static/images/features/corpstats/eve_sso_authorization.png)

You will return to auth where you are asked to select a token with the green arrow button. If you want to use a different character, press the `LOG IN with EVE Online` button.

![select an SSO token to create with](/_static/images/features/corpstats/select_sso_token.png)

If this works (and you have permission to view the Corp Stats you just created) you'll be returned to a view of the Corp Stats.
If it fails an error message will be displayed.

## Corp Stats View

### Navigation Bar

![navigation bar](/_static/images/features/corpstats/navbar.png)

This bar contains a dropdown menu of all available corps. If the user has the `add_corpstats` permission, a button to add a Corp Stats will be shown.

On the right of this bar is a search field. Press enter to search. It checks all characters in all Corp Stats you have view permission to and returns search results.

### Last Update

![last update and update button](/_static/images/features/corpstats/last_update.png)

An update can be performed immediately by pressing the update button. Anyone who can view the Corp Stats can update it. 

### Character Lists

![lists](/_static/images/features/corpstats/lists.png)

Three views are available:
 - main characters and their alts
 - registered characters and their main character
 - unregistered characters

Each view contains a sortable and searchable table. The number of listings shown can be increased with a dropdown selector. Pages can be changed using the controls on the bottom-right of the table. Each list is searchable at the top-right. Tables can be re-ordered by clicking on column headings.

![table control locations](/_static/images/features/corpstats/table_controls.png)

#### Main List

![main list](/_static/images/features/corpstats/main_list.png)

This list contains all main characters in registered in the selected corporation and their alts. Each character has a link to [zKillboard](https://zkillboard.com).


#### Member List

![member list](/_static/images/features/corpstats/member_list.png)

The list contains all characters in the corp. Red backgrounds means they are not registered in auth. A link to [zKillboard](https://zkillboard.com) is present for all characters.
If registered, the character will also have a main character, main corporation, and main alliance field.

#### Unregistered List

![unregistered_list](/_static/images/features/corpstats/unregistered_list.png)

This list contains all characters not registered on auth. Each character has a link to [zKillboard](https://zkillboard.com).

## Search View

![search results](/_static/images/features/corpstats/search_view.png)

This view is essentially the same as the Corp Stats page, but not specific to a single corp.
The search query is visible in the search box.
Characters from all Corp Stats to which the user has view access will be displayed. APIs respect permissions.


## Permissions

To use this feature, users will require some of the following:

```eval_rst
+---------------------------------------+------------------+----------------------------------------------------+
| Permission                            | Admin Site       | Auth Site                                          |
+=======================================+==================+====================================================+
| corpstats.view_corp_corpstats         | None             | Can view corp stats of their corporation.          |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.view_alliance_corpstats     | None             | Can view corp stats of members of their alliance.  |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.view_state_corpstats        | None             | Can view corp stats of members of their auth state.|
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.add_corpstats               | Can create model | Can add new corpstats using an SSO token.          |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.change_corpstats            | Can edit model   | None.                                              |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.remove_corpstats            | Can delete model | None.                                              |
+---------------------------------------+------------------+----------------------------------------------------+

```

Users who add a Corp Stats with their token will be granted permissions to view it regardless of the above permissions. View permissions are interpreted in the "OR" sense: a user can view their corp's Corp Stats without the `view_corp_corpstats` permission if they have the `view_alliance_corpstats` permission, same idea for their state. Note that these evaluate against the user's main character.

## Automatic Updating
By default Corp Stats are only updated on demand. If you want to automatically refresh on a schedule, add an entry to your project's settings file:

    CELERYBEAT_SCHEDULE['update_all_corpstats'] = {
        'task': 'allianceauth.corputils.tasks.update_all_corpstats',
        'schedule': crontab(minute=0, hour="*/6"),
    }

Adjust the crontab as desired.

## Troubleshooting

### Failure to create Corp Stats

>Unrecognized corporation. Please ensure it is a member of the alliance or a blue.

Corp Stats can only be created for corporations who have a model in the database. These only exist for tenant corps,
corps of tenant alliances, blue corps, and members of blue alliances.

>Selected corp already has a statistics module.

Only one Corp Stats may exist at a time for a given corporation.

>Failed to gather corporation statistics with selected token.

During initial population, the EVE Swagger Interface did not return any member data. This aborts the creation process. Please wait for the API to start working before attempting to create again.

### Failure to update Corp Stats

Any of the following errors will result in a notification to the owning user, and deletion of the Corp Stats model.

>Your token has expired or is no longer valid. Please add a new one to create a new CorpStats.

This occurs when the SSO token is invalid, which can occur when deleted by the user, the character is transferred between accounts, or the API is having a bad day.

>CorpStats for (corp name) cannot update with your ESI token as you have left corp.

The SSO token's character is no longer in the corp which the Corp Stats is for, and therefore membership data cannot be retrieved.

>HTTPForbidden

The SSO token lacks the required scopes to update membership data.
