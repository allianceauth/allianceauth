# Settings Overview

The `alliance_auth/settings.py` file is used to pass settings to the django app needed to run.

### Words of Warning

Certain fields are quite sensitive to leading `http://` and trailing `/` - if you see these present in the default text, be sure to include them in your values.

Every variable value is opened and closed with a single apostrophe `'` - please do not include these in your values or it will break things. If you absolutely must, replace them at the opening and closing of the value with double quotes `"`.

Certain variables are booleans, and come in a form that looks like this:

    MEMBER_CORP_GROUPS = 'True' == os.environ.get('AA_MEMBER_CORP_GROUPS', 'True')

They're handled as strings because when settings are exported from shell commands (eg `export AA_MEMBER_CORP_GROUPS False`) they're interpreted as strings, so a string comparison is done.

When changing these booleans, edit the setting within the brackets (eg `('AA_MEMBER_CORP_GROUPS', 'True')` vs `('AA_MEMBER_CORP_GROUPS', 'False')`) and not the `True` earlier in the statement. Otherwise these will have unexpected behaviours.

# Fields to Modify

## Required
 - [SECRET_KEY](#secret-key)
   - Use [this tool](http://www.miniwebtool.com/django-secret-key-generator/) to generate a key on initial install
 - [DEBUG](#debug)
   - If issues are encountered, set this to `True` to view a more detailed error report, otherwise set `False`
 - [ALLOWED_HOSTS](#allowed-hosts)
   - This restricts web addresses auth will answer to. Separate with commas. 
   - Should include localhost `127.0.0.1` and `example.com`
   - To allow from all, include `'*'`
 - [DATABASES](#databases)
   - Fill out the database name and user credentials to manage the auth database.
 - [DOMAIN](#domain)
   - Set to the domain name AllianceAuth will be accessible under
 - [EMAIL_HOST_USER](#email-host-user)
   - Username to send emails from. If gmail account, the full gmail address.
 - [EMAIL_HOST_PASSWORD](#email-host-password)
   - Password for the email user.
 - [CORP_IDS](#corp-ids)
   - List of corp IDs who are members. Exclude if their alliance is in `ALLIANCE_IDS`
 - [ALLIANCE_IDS](#alliance-ids)
   - List of alliance IDs who are members.
 - [ESI_SSO_CLIENT_ID](#esi-sso-client_id)
   - EVE application ID from the developers site. See the [SSO Configuration Instruction](#sso-settings)
 - [ESI_SSO_CLIENT_SECRET](#esi-sso-client-secret)
   - EVE application secret from the developers site.
 - [ESI_SSO_CALLBACK_URL](#esi-sso-callback-url)
   - OAuth callback URL. Should be `https://mydomain.com/sso/callback`

## Services
### IPBoard
If using IPBoard, the following need to be set in accordance with the [install instructions](../services/ipboard3.md)
 - [IPBOARD_ENDPOINT](#ipboard-endpoint)
 - [IPBOARD_APIKEY](#ipboard-apikey)
 - [IPBOARD_APIMODULE](#ipboard-apimodule)

### XenForo
If using XenForo, the following need to be set in accordance with the [install instructions](../services/xenforo.md)
 - [XENFORO_ENDPOINT](#xenforo-endpoint)
 - [XENFORO_APIKEY](#xenforo-apikey)

### Openfire
If using Openfire, the following need to be set in accordance with the [install instructions](../services/openfire.md)
 - [JABBER_URL](#jabber-url)
 - [JABBER_PORT](#jabber-port)
 - [JABBER_SERVER](#jabber-server)
 - [OPENFIRE_ADDRESS](#openfire-address)
 - [OPENFIRE_SECRET_KEY](#openfire-secret-key)
 - [BROADCAST_USER](#broadcast-user)
 - [BROADCAST_USER_PASSWORD](#broadcast-user-password)
 - [BROADCAST_SERVICE_NAME](#broadcast-service-name)
 - [BROADCAST_IGNORE_INVALID_CERT](#broadcast-ignore-invalid-cert)

### Mumble
If using Mumble, the following needs to be set to the address of the mumble server:
 - [MUMBLE_URL](#mumble-url)

### PHPBB3
If using phpBB3, the database needs to be defined.

### Teamspeak3
If using Teamspeak3, the following need to be set in accordance with the [install instrictions](../services/teamspeak3.md)
 - [TEAMSPEAK3_SERVER_IP](#teamspeak3-server-ip)
 - [TEAMSPEAK3_SERVER_PORT](#teamspeak3-server-port)
 - [TEAMSPEAK3_SERVERQUERY_USER](#teamspeak3-serverquery-user)
 - [TEAMSPEAK3_SERVERQUERY_PASSWORD](#teamspeak3-serverquery-password)
 - [TEAMSPEAK3_VIRTUAL_SERVER](#teamspeak3-virtual-server)
 - [TEAMSPEAK3_PUBLIC_URL](#teamspeak3-public-url)

### Discord
If connecting to a Discord server, set the following in accordance with the [install instructions](../services/discord.md)
 - [DISCORD_GUILD_ID](#discord-guild-id)
 - [DISCORD_BOT_TOKEN](#discord-bot-token)
 - [DISCORD_INVITE_CODE](#discord-invite-code)
 - [DISCORD_APP_ID](#discord-app-id)
 - [DISCORD_APP_SECRET](#discord-app-secret)
 - [DISCORD_CALLBACK_URL](#discord-callback-url)
 - [DISCORD_SYNC_NAMES](#discord-sync-names)

### Discourse
If connecting to Discourse, set the following in accordance with the [install instructions](../services/discourse.md)
 - [DISCOURSE_URL](#discourse-url)
 - [DISCOURSE_API_USERNAME](#discourse-api-username)
 - [DISCOURSE_API_KEY](#discourse-api-key)
 - [DISCOURSE_SSO_SECRET](#discourse-sso-secret)

### IPSuite4
If using IPSuite4 (aka IPBoard4) the following are required:
 - [IPS4_URL](#ips4-url)
 - the database needs to be defined

### SMF
If using SMF the following are required:
 - [SMF_URL](#smf-url)
 - the database needs to be defined

## Optional
### Standings
To allow access to blues, a corp API key is required to pull standings from. Corp does not need to be owning corp or in owning alliance. Required mask is 16 (Communications/ContactList)
 - [CORP_API_ID](#corp-api-id)
 - [CORP_API_VCODE](#corp-api-vcode)

### API Key Audit URL
To define what happens when an API is clicked, set according to [these instructions](#hr-configuration)
 - [API_KEY_AUDIT_URL](#api-key-audit-url)

### Auto Groups
Groups can be automatically assigned based on a user's corp or alliance. Set the following to `True` to enable this feature.
 - [MEMBER_CORP_GROUPS](#member-corp-groups)
 - [MEMBER_ALLIANCE_GROUPS](#member-alliance-groups)
 - [BLUE_CORP_GROUPS](#blue-corp-groups)
 - [BLUE_ALLIANCE_GROUPS](#blue-alliance-groups)

### Fleet-Up
Fittings and operations can be imported from Fleet-Up. Define the following to do so.
 - [FLEETUP_APP_KEY](#fleetup-app-key)
 - [FLEETUP_USER_ID](#fleetup-user-id)
 - [FLEETUP_API_ID](#fleetup-api-id)
 - [FLEETUP_GROUP_ID](#fleetup-group-id)

### CAPTCHA
To help prevent bots from registering and brute forcing the login. Get the reCaptcha keys from [here](https://www.google.com/recaptcha/intro/index.html)
 - [CAPTCHA_ENABLED](#captcha_enabled)
 - [RECAPTCHA_PUBLIC_KEY](#recaptcha_public_key)
 - [RECAPTCHA_PRIVATE_KEY](#recaptcha_private_key)
 - [NOCAPTCHA](#nocaptcha)

# Description of Settings
## Django
### SECRET_KEY
A random string used in cryptographic functions, such as password hashing. Changing after installation will render all sessions and password reset tokens invalid.
### DEBUG
Replaces the generic `SERVER ERROR (500)` page when an error is encountered with a page containing a traceback and variables. May expose sensitive information so not recommended for production.
### ALLOWED_HOSTS
A list of addresses used to validate headers: AllianceAuth will block connection coming from any other address. This should be a list of URLs and IPs to allow. In most cases, just adding `'example.com'` is sufficient. This also accepts the `'*'` wildcard for testing purposes.
### DATABASES
List of databases available. Contains the Django database, and may include service ones if enabled. Service databases are defined in their individual sections and appended as needed automatically.
### LANGUAGE_CODE
Friendly name of the local language.
### TIME_ZONE
Friendly name of the local timezone.
### CAPTCHA_ENABLED
Enable Google reCaptcha
### RECAPTCHA_PUBLIC_KEY
Google reCaptcha public key
### RECAPTCHA_PRIVATE_KEY
Google reCaptcha private key
### NOCAPTCHA
Enable New No Captcha reCaptcha
### STATIC_URL
Absolute URL to serve static files from.
### STATIC_ROOT
Root folder to store static files in.
### SUPERUSER_STATE_BYPASS
Overrides superuser account states to always return True on membership tests. If issues are encountered, or you want to test access to certain portions of the site, set to False to respect true states of superusers.
## EMAIL SETTINGS
### DOMAIN
The URL to which emails will link.
### EMAIL_HOST
The host address of the email server.
### EMAIL_PORT
The host port of the email server.
### EMAIL_HOST_USER
The username to authenticate as on the email server. For GMail, this is the full address.
### EMAIL_HOST_PASSWORD
The password of the user used to authenticate on the email server.
### EMAIL_USE_TLS
Enable TLS connections to the email server. Default is True.
## Front Page Links
### KILLBOARD_URL
Link to a killboard.
### EXTERNAL_MEDIA_URL
Link to another media site, eg YouTube channel.
### FORUM_URL
Link to forums. Also used as the phpbb3 URL if enabled.
### SITE_NAME
Name to show in the top-left corner of auth.
## SSO Settings
An application will need to be created on the developers site. Please select `Authenticated API Access`, and choose all scopes starting with `esi`.
### ESI_SSO_CLIENT_ID
The application cliend ID generated from the [developers site.](https://developers.eveonline.com)
### ESI_SSO_CLIENT_SECRET
The application secret key generated from the [developers site.](https://developers.eveonline.com)
### ESI_SSO_CALLBACK_URL
The callback URL for authentication handshake. Should be `https://example.com/sso/callback`.
## Default Group Settings
### DEFAULT_AUTH_GROUP
Name of the group members of the owning corp or alliance are put in.
### DEFAULT_BLUE_GROUP
Name of the group blues of the owning corp or alliance are put in.
### MEMBER_CORP_GROUPS
If `True`, add members to groups with their corp name, prefixed with `Corp_`
### MEMBER_ALLIANCE_GROUPS
If `True`, add members to groups with their alliance name, prefixed with `Alliance_`
### BLUE_CORP_GROUPS
If `True`, add blues to groups with their corp name, prefixed with `Corp_`
### BLUE_ALLIANCE_GROUPS
If `True`, add blues to groups with their alliance name, prefixed with `Alliance_`
## Alliance Service Setup
### ENABLE_AUTH_FORUM
Allow members of the owning corp or alliance to generate accounts on a Phpbb3 install.
### ENABLE_AUTH_JABBER
Allow members of the owning corp or alliance to generate accounts on an Openfire install.
### ENABLE_AUTH_MUMBLE
Allow members of the owning corp or alliance to generate accounts on a Mumble install.
### ENABLE_AUTH_IPBOARD
Allow members of the owning corp or alliance to generate accounts on an IPBoard install.
### ENABLE_AUTH_TEAMSPEAK3
Allow members of the owning corp or alliance to generate accounts on a Teamspeak3 install.
### ENABLE_AUTH_DISCORD
Allow members of the owning corp or alliance to link accounts to a Discord server.
### ENABLE_AUTH_DISCOURSE
Allow members of the owning corp or alliance to generate accounts on a Discourse install
### ENABLE_AUTH_IPS4
Allow members of the owning corp or alliance to generate accounts on a IPSuite4 install.
### ENABLE_AUTH_SMF
Allow members of the owning corp or alliance to generate accounts on a SMF install.
### ENABLE_AUTH_MARKET
Allow members of the owning corp or alliance to generate accounts on an alliance market install.
### ENABLE_AUTH_XENFORO
Allow members of the owning corp or alliance to generate accounts on a XenForo install.
## Blue Service Setup
### ENABLE_BLUE_FORUM
Allow blues of the owning corp or alliance to generate accounts on a Phpbb3 install.
### ENABLE_BLUE_JABBER
Allow blues of the owning corp or alliance to generate accounts on an Openfire install.
### ENABLE_BLUE_MUMBLE
Allow blues of the owning corp or alliance to generate accounts on a Mumble install.
### ENABLE_BLUE_IPBOARD
Allow blues of the owning corp or alliance to generate accounts on an IPBoard install.
### ENABLE_BLUE_TEAMSPEAK3
Allow blues of the owning corp or alliance to generate accounts on a Teamspeak3 install.
### ENABLE_BLUE_DISCORD
Allow blues of the owning corp or alliance to link accounts to a Discord server.
### ENABLE_BLUE_DISCOURSE
Allow blues of the owning corp or alliance to generate accounts on a Discourse install.
### ENABLE_BLUE_IPS4
Allow blues of the owning corp or alliance to generate accounts on an IPSuite4 install.
### ENABLE_BLUE_SMF
Allow blues of the owning corp or alliance to generate accounts on a SMF install.
### ENABLE_BLUE_MARKET
Allow blues of the owning corp or alliance to generate accounts on an alliance market install.
### ENABLE_BLUE_XENFORO
Allow blues of the owning corp or alliance to generate accounts on a XenForo install.
## Tenant Configuration
Characters of any corp or alliance with their ID here will be treated as a member.
### CORP_IDS
EVE corp IDs of member corps. Separate with a comma.
### ALLIANCE_IDS
EVE alliance IDs of member alliances. Separate with a comma.
## Standings Configuration
To allow blues to access auth, standings must be pulled from a corp-level API. This API needs access mask 16 (ContactList).
### CORP_API_ID
The ID of an API key for a corp from which to pull standings, if desired. Needed for blues to gain access.
### CORP_API_VCODE
The verification code of an API key for a corp from which to pull standings, if desired. Needed for blues to gain access.
### BLUE_STANDING
The minimum standing value to consider blue. Default is 5.0
### STANDING_LEVEL
Standings from the API come at two levels: `corp` and `alliance`. Select which level to consider here.
## API Configuration
### MEMBER_API_MASK
Required access mask for members' API keys to be considered valid.
### MEMBER_API_ACCOUNT
If `True`, require API keys from members to be account-wide, not character-restricted.
### BLUE_API_MASK
Required access mask for blues' API keys to be considered valid.
### BLUE_API_ACCOUNT
If `True`, require API keys from blues to be account-wide, not character-restricted.
### REJECT_OLD_APIS
Require each submitted API be newer than the latest submitted API. Protects against recycled or stolen API keys.
### REJECT_OLD_APIS_MARGIN
Allows newly submitted APIs to have their ID this value lower than the highest API ID on record and still be accepted. Default is 50, 0 is safest.
## EVE Provider Settings
Data about EVE objects (characters, corps, alliances) can come from two sources: the XML API or the EVE Swagger Interface.
These settings define the default source.

For most situations, the EVE Swagger Interface is best. But if it goes down or experiences issues, these can be reverted to the XML API.

Accepted values are `esi` and `xml`.
### EVEONLINE_CHARACTER_PROVIDER
The default data source to get character information. Default is `esi`
### EVEONLINE_CORP_PROVIDER
The default data source to get corporation information. Default is `esi`
### EVEONLINE_ALLIANCE_PROVIDER
The default data source to get alliance information. Default is `esi`
### EVEONLINE_ITEMTYPE_PROVIDER
The default data source to get item type information. Default is `esi`
## Alliance Market
### MARKET_URL
The web address to access the Evernus Alliance Market application.
### MARKET_DB
The Evernus Alliance Market database connection information.
## HR Configuration
### API_KEY_AUDIT_URL
This setting defines what happens when someone clicks on an API key (such as in corpstats or an application).

Default behaviour is to show the verification code in a popup, but this can be set to link out to a website.

The URL set here uses python string formatting notation. Variable names are enclosed in `{}` brackets. Three variable names are available: `api_id`, `vcode`, and `pk` (which is the primary key of the API in the database - only useful on the admin site).

Example URL structures are provided. Jacknife can be installed on your server following [its setup guide.](../services/jacknife.md)
## IPBoard3 Configuration
### IPBOARD_ENDPOINT
URL to the `index.php` file of a IPBoard install's API server.
### IPBOARD_APIKEY
API key for accessing an IPBoard install's API
### IPBOARD_APIMODULE
Module to access while using the API
## XenForo Configuration
### XENFORO_ENDPOINT
The address of the XenForo API. Should look like `https://example.com/forum/api.php`
### XENFORO_DEFAULT_GROUP
The group ID of the group to assign to member. Default is 0.
### XENFORO_APIKEY
The API key generated from XenForo to allow API access.
## Jabber Configuration
### JABBER_URL
Address to instruct members to connect their jabber clients to, in order to reach an Openfire install. Usually just `example.com`
### JABBER_PORT
Port to instruct members to connect their jabber clients to, in order to reach an Openfire install. Usually 5223.
### JABBER_SERVER
Server name of an Openfire install. Usually `example.com`
### OPENFIRE_ADDRESS
URL of the admin web interface for an Openfire install. Usually `http://example.com:9090`. If HTTPS is desired, change port to 9091: `https://example.com:9091`
### OPENFIRE_SECRET_KEY
Secret key used to authenticate with an Openfire admin interface.
### BROADCAST_USER
Openfire user account used to send broadcasts from. Default is `Broadcast`.
### BROADCAST_USER_PASSWORD
Password to use when authenticating as the `BROADCAST_USER`
### BROADCAST_SERVICE_NAME
Name of the broadcast service running on an Openfire install. Usually `broadcast`
## Mumble Configuration
### MUMBLE_URL
Address to instruct members to connect their Mumble clients to.
### MUMBLE_SERVER_ID
Depreciated. We're too scared to delete it.
## Teamspeak3 Configuration
### TEAMSPEAK3_SERVER_IP
IP of a Teamspeak3 server on which to manage users. Usually `127.0.0.1`
### TEAMSPEAK3_SERVER_PORT
Port on which to connect to a Teamspeak3 server at the `TEAMSPEAK3_SERVER_IP`. Usually `10011`
### TEAMSPEAK3_SERVERQUERY_USER
User account with which to authenticate on a Teamspeak3 server. Usually `serveradmin`.
### TEAMSPEAK3_SERVERQUERY_PASSWORD
Password to use when authenticating as the `TEAMSPEAK3_SERVERQUERY_USER`. Provided during first startup or when you define a custom serverquery user.
### TEAMSPEAK3_VIRTUAL_SERVER
ID of the server on which to manage users. Usually `1`.
### TEAMSPEAK3_PUBLIC_URL
Address to instruct members to connect their Teamspeak3 clients to. Usually `example.com`
## Discord Configuration
### DISCORD_GUILD_ID
The ID of a Discord server on which to manage users.
### DISCORD_BOT_TOKEN
The bot token obtained from defining a bot on the [Discord developers site.](https://discordapp.com/developers/applications/me)
### DISCORD_INVITE_CODE
A no-limit invite code required to add users to the server. Must be generated from the Discord server itself (instant invite).
### DISCORD_APP_ID
The application ID obtained from defining an application on the [Discord developers site.](https://discordapp.com/developers/applications/me)
### DISCORD_APP_SECRET
The application secret key obtained from defining an application on the [Discord developers site.](https://discordapp.com/developers/applications/me)
### DISCORD_CALLBACK_URL
The callback URL used for authenticaiton flow. Should be `https://example.com/discord_callback`. Must match exactly the one used when defining the application.
### DISCORD_SYNC_NAMES
Override usernames on the server to match the user's main character.
## Discourse Configuration
### DISCOURSE_URL
The web address of the Discourse server to direct users to.
### DISCOURSE_API_USERNAME
Username of the account which generated the API key on Discourse.
### DISCOURSE_API_KEY
API key defined on Discourse.
### DISCOURSE_SSO_SECRET
The SSO secret key defined on Discourse.
## IPS4 Configuration
### IPS4_URL
URL of the IPSuite4 install to direct users to.
### IPS4_API_KEY
Depreciated. We're too scared to delete it.
### IPS4_DB
The database connection to manage users on.
## SMF Configuration
### SMF_URL
URL of the SMF install to direct users to.
### SMF_DB
The database connection to manage users on.
## Fleet-Up Configuration
### FLEETUP_APP_KEY
Application key as [defined on Fleet-Up.](http://fleet-up.com/Api/MyApps)
### FLEETUP_USER_ID
API user ID as [defined on Fleet-Up.](http://fleet-up.com/Api/MyKeys)
### FLEETUP_API_ID
API ID as [defined on Fleet-Up.](http://fleet-up.com/Api/MyKeys)
### FLEETUP_GROUP_ID
The group ID from which to pull data. Can be [retrieved from Fleet-Up](http://fleet-up.com/Api/Endpoints#groups_mygroupmemberships)
## Logging Configuration
This section is used to manage how logging messages are processed.

To turn off logging notifications, change the `handlers` `notifications` `class` to `logging.NullHandler`

## Danger Zone
Everything below logging is magic. **Do not touch.**
