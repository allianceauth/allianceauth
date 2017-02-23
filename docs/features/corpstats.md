# Corp Stats

This module is used to check the registration status of corp members and to determine character relationships, being mains or alts.

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

On the right of this bar is a search field. Press enter to search. It checks all characters in all Corp Stats you have view permission to and returns search results. Generic searches (such as 'a') will be slow.

### API Index

![API Index](/_static/images/features/corpstats/api_index.png)

This is a visual indication of the number of registered characters.

### Last Update

![last update and update button](/_static/images/features/corpstats/last_update.png)

Corp Stats do not automatically update. They update once upon creation for initial data, and whenever someone presses the update button.

Only superusers and the creator of the Corp Stat can update it.

### Member List

![member list](/_static/images/features/corpstats/member_list.png)

The list contains all characters in the corp. Red backgrounds means they are not registered in auth. If registered, and the user has the required permission to view APIs, a link to JackKnife will be present.
A link to zKillboard is present for all characters.
If registered, the character will also have a main character, main corporation, and main alliance field.

This view is paginated: use the navigation arrows to view more pages (sorted alphabetically by character name), or search for a specific character.

![pagination buttons](/_static/images/features/corpstats/pagination.png)

## Search View

![search results](/_static/images/features/corpstats/search_view.png)

This view is essentially the same as the Corp Stats page, but not specific to a single corp.
The search query is visible in the search box.
Characters from all Corp Stats to which the user has view access will be displayed. APIs respect permissions.

This view is paginated: use the navigation arrows to view more pages (sorted alphabetically by character name).

## Permissions

To use this feature, users will require some of the following:

```eval_rst
+---------------------------------------+------------------+----------------------------------------------------+
| Permission                            | Admin Site       | Auth Site                                          |
+=======================================+==================+====================================================+
| corpstats.corp_apis                   | None             | Can view API keys of members of their corporation. |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.alliance_apis               | None             | Can view API keys of members of their alliance.    |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.blue_apis                   | None             | Can view API keys of members of blue corporations. |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.view_corp_corpstats         | None             | Can view corp stats of their corporation.          |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.view_alliance_corpstats     | None             | Can view corp stats of members of their alliance.  |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.view_blue_corpstats         | None             | Can view corp stats of blue corporations.          |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.add_corpstats               | Can create model | Can add new corpstats using an SSO token.          |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.change_corpstats            | Can edit model   | None.                                              |
+---------------------------------------+------------------+----------------------------------------------------+
| corpstats.remove_corpstats            | Can delete model | None.                                              |
+---------------------------------------+------------------+----------------------------------------------------+

```

Typical use-cases would see the bundling of `corp_apis` and `view_corp_corpstats`, same for alliances and blues.
Alliance permissions supersede corp permissions. Note that these evaluate against the user's main character.

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

>CorpStats for corp_name cannot update with your ESI token as you have left corp.

The SSO token's character is no longer in the corp which the Corp Stats is for, and therefore membership data cannot be retrieved.

>HTTPForbidden

The SSO token lacks the required scopes to update membership data.
