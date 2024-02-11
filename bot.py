import os
import discord
from discord import app_commands
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_token():
    token_key = 'COM_GABBRO_DISCORD_TOKEN'
    token = os.getenv(token_key)
    if token is None:
        raise Exception(f'Missing environment variable {token_key}')
    return token

def create_client():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        logger.info(f'{client.user} has connected to Discord')

        synced = await tree.sync()
        logger.info(f'Synced {len(synced)} command(s)')

    @tree.command(name="hello")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f'Hello {interaction.user.mention}!')

    return client

def main():
    token = get_token()
    client = create_client()
    client.run(token)

if __name__ == '__main__':
    main()
