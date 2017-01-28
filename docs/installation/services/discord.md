# Discord
## Overview
Discord is a web-based instant messaging client with voice. Kind of like teamspeak meets slack meets skype. It also has a standalone app for phones and desktop.

## Setup

Add `services.modules.discord` to your `INSTALLED_APPS` list and run migrations before continuing with this guide to ensure the service is installed.

### Creating a Server
*If you already have a Discord server, skip the creation step, but be sure to retrieve the server ID and enter it in settings.py*

Navigate to the [Discord site](https://discordapp.com/) and register an account, or log in if you have one already.

On the left side of the screen you’ll see a circle with a plus sign. This is the button to create a new server. Go ahead and do that, naming it something obvious.

Now retrieve the server ID from the URL of the page you’re on. The ID is the first of the very long numbers. For instance my testing server’s url look like:

    https://discordapp.com/channels/120631096835571712/120631096835571712

with a server ID of `120631096835571712`

Update settings.py, inputting the server ID as `DISCORD_GUILD_ID`

### Generating an Invite
Still on the Discord site, in your new server, an invite needs to be generated for users to join. If you with for users to  initially join a different channel than `#general`, create it and follow the steps below, substituting this channel for `#general`.

On the left bar under the Text Channels heading, hover over `#general` on the right site. There are two icons, a box with an arrow and a gear. Press the box, then on the bottom left select Advanced Settings. Set the expiration to never, and no limit on uses. Press generate.

This returns a code that looks like `https://discord.gg/0fmA8MyXV6qt7XAZ`. The part after the last slash, `0fmA8MyXV6qt7XAZ`, is the invite code. Update settings.py, inputting this invite code as `DISCORD_INVITE_CODE`

### Registering an Application

Navigate to the [Discord Developers site.](https://discordapp.com/developers/applications/me) Press the plus sign to create a new application.

Give it a name and description relating to your auth site. Add a redirect to `https://example.com/discord/callback/`, substituting your domain. Press Create Application.

Update settings.py, inputting this redirect address as `DISCORD_CALLBACK_URL`

On the application summary page, press Create a Bot User.

Update settings.py with these pieces of information from the summary page:
 - From the App Details panel, `DISCORD_APP_ID` is the Client/Application ID
 - From the App Details panel, `DISCORD_APP_SECRET` is the Secret
 - From the App Bot Users panel, `DISCORD_BOT_TOKEN` is the Token

### Adding a Bot to the Server
Once created, navigate to the services page of your AllianceAuth install as the superuser account. At the top there is a big green button labelled Link Discord Server. Click it, then from the drop down select the server you created, and then Authorize.

This adds a new user to your Discord server with a `BOT` tag, and a new role with the same name as your Discord application. Don't touch either of these. If for some reason the bot loses permissions or is removed from the server, click this button again.

To manage roles, this bot role must be at the top of the hierarchy. Edit your Discord server, roles, and click and drag the role with the same name as your application to the top of the list. This role must stay at the top of the list for the bot to work.  Finally, the owner of the bot account must enable 2 Factor Authentication (this is required from discord for kicking and modifying member roles).  If you are unsure what 2FA is or how to set it up, refer to [this support page](https://support.discordapp.com/hc/en-us/articles/219576828).  It is also recommended to force 2fa on your server (this forces any admins or moderators to have 2fa enabled to perform similar functions on discord).

### Linking Accounts
Instead of the usual account creation procedure, for Discord to work we need to link accounts to AllianceAuth. When attempting to enable the Discord service, users are redirected to the official Discord site to authenticate. They will need to create an account if they don't have one prior to continuing. Upon authorization, users are redirected back to AllianceAuth with an OAuth code which is used to join the Discord server.

## Managing Roles
Once users link their accounts you’ll notice Roles get populated on Discord. These are the equivalent to Groups on every other service. The default permissions should be enough for members to chat and use comms. Add more permissions to the roles as desired through the server management window.
