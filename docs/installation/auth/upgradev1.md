# Upgrading from v1.15

It's possible to preserve a v1 install's database and migrate it to v2. This will retain all service accounts, user accounts with their main character, but will purge API keys and alts.

## Preparing to Upgrade

Ensure your auth install is at least version 1.15 - it's preferred to be on v1.15.8 but any v1.15.x should work. If not, update following normal procedures and ensure you run migrations.

If you will not be using any apps (or they have been removed in v2) clear their database tables before beginning the v2 install procedure. From within your v1 install, `python manage.py migrate APPNAME zero`, replacing `APPNAME` with the appropriate name.

It's strongly encouraged to perform the upgrade with a **copy** of the original v1 database. If something goes wrong this allows you to roll back and try again. This can be achieved with:

    mysqldump -u root -p v1_database_name_here | mysql -u root -p v2_database_name_here

Note this command will prompt you for the root password twice.

Alliance Auth v2 requires Python 3.4 or newer. If this is not available on your system be sure to install the [dependencies listed.](allianceauth.md#python)

## Installation

Follow the [normal install procedures for Alliance Auth v2](allianceauth.md). If you're coming from v1 you likely already have the user account and dependencies.

When configuring settings, ensure to enter the database information relating to the copy you made of the v1 database, but **do not run migrations**. See below before continuing.

Do not start Celery yet.

## Migration

During the upgrade process a migration is run which ports data to the new system. Its behaviour can be configured through some optional settings.

### User Accounts

A database migration is included to port users to the new SSO-based login system. It will automatically assign states and main characters.

Password for non-staff accounts are destroyed so they cannot be used to log in - only SSO is available for regular members. Staff can login using username and password through the admin site or by SSO.

### EVE Characters

Character ownership is now tracked by periodically validating a refreshable SSO token. When migrating from v1 not all users may have such a refreshable token: to allow these users to retain their existing user account their main character is set to the one present in v1, bypassing this validation mechanism.

It is essential to get your users to log in via SSO soon after migration to ensure their accounts are managed properly. Any user who does not log in will not lose their main character under any circumstance, even character sale. During a sale characters are transferred to an NPC corp - get celery tasks running within 24 hours of migration so that during a sale the user loses their state (and hence permissions). This can be an issue if you've granted service access permissions to a user or their groups: it's strongly encouraged to grant service access by state from now on.

Because character ownership is tracked separately of main character it is not possible to preserve alts unless a refreshable SSO token is present for them.

### Members and Blues

The new [state system](../../features/states.md) allows configuring dynamic membership states through the admin page. Unfortunately if you make a change after migrating it will immediately assess user states and see that no one should be a member. You can add additional settings to your auth project's settings file to generate the member and blue states as you have them defined in v1:
 - `ALLIANCE_IDS = []` a list of member alliance IDs
 - `CORP_IDS = []` a list of member corporation IDs
 - `BLUE_ALLIANCE_IDS = []` a list of blue alliance IDs
 - `BLUE_CORP_IDS = []` a list of blue corporation IDs

Put comma-separated IDs into the brackets and the migration will create states with the members and blues you had before. This will prevent unexpected state purging when you edit states via the admin site.

### Default Groups

If you used member/blue group names other than the standard "Member" and "Blue" you can enter settings to have the member/blue states created through this migration take these names.
 - `DEFAULT_AUTH_GROUP = ""` the desired name of the "Member" state
 - `DEFAULT_BLUE_GROUP = ""` the desired name of the "Blue" state 

Any permissions assigned to these groups will be copied to the state replacing them. Because these groups are no longer managed they pose a security risk and so are deleted at the end of the migration automatically.

### Run Migrations

Once you've configured any optional settings it is now safe to run the included migrations.

## Validating Upgrade

Before starting the Celery workers it's a good idea to validate the states were created and assigned correctly. Any mistakes now will trigger deletion of service accounts: if Celery workers aren't running these tasks aren't yet processed. States can be checked through the admin site.

The site (and not Celery) can be started with `supervisorctl start myauth:gunicorn`. Then navigate to the admin site and log in with your v1 username and password. States and User Profiles can be found under the Authentication app.

Once you have confirmed states are correctly configured (or adjusted them as needed) clear the Celery task queue: from within your auth project folder, `celery -A myauth purge`

It should now be safe to bring workers online (`supervisorctl start myauth:`) and invite users to use the site.

## Help

If something goes wrong during the migration reach out for help on [Gitter](https://gitter.im/R4stl1n/allianceauth) or open an [issue](https://github.com/allianceauth/allianceauth/issues).