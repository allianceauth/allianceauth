import discord
from django.conf import settings


client = discord.Client()

print('Logging in to Discord as ' + settings.DISCORD_USER_EMAIL)
client.login(settings.DISCORD_USER_EMAIL, settings.DISCORD_USER_PASSWORD)
if not client.is_logged_in:
    print('Logging in to Discord failed')
    raise ValueError('Supplied Discord credentials failed login')

@client.event
def on_ready():
    server = client.servers[0]
    user = client.user
    print('Connected as ' + user.name)
