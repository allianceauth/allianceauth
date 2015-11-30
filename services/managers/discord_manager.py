from services.managers.util import discord_client
from django.conf import settings

class DiscordManager:
    def __init__(self, discord_client):
        self.discord_client = discord_client
        discord_client.client.run()
        super().__init__()
