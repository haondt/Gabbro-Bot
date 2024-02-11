import environment
import discord
from discord import app_commands
import logging
import gabbro_docker as docker
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State():
    def __init__(self):
        self.containers: list[str]|None = None
        self.containers_stale = False

    def stale_containers(self):
        self.containers_stale = True

    def get_containers(self):
        if self.containers is None or self.containers_stale:
            self.containers = docker.get_containers()
            self.containers_stale = False
        return self.containers


class Status(Enum):
    STARTED = 0,
    FINISHED = 1,
    FAILED = 2
class StatusMessage():
    def __init__(self, title: str):
        self.status: Status = Status.STARTED
        self.title = title
        self.logs = ''
    def add_logs(self, logs):
        self.logs += logs

    def render(self):
        status_symbol = {
                Status.STARTED: '⏳',
                Status.FINISHED: '✅',
                Status.FAILED: '❌'
                }[self.status]
        output_strs = [f'**{self.title}** {status_symbol}']
        if len(self.logs) > 0:
            output_strs.append(f'```{self.logs}```')
        return '\n'.join(output_strs)
    def finish(self):
        self.status = Status.FINISHED
        return self.render()
    def fail(self):
        self.status = Status.FAILED
        return self.render()

state = State()

def create_client():
    intents = discord.Intents.default()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        logger.info(f'{client.user} has connected to Discord')

        synced = await tree.sync()
        logger.info(f'Synced {len(synced)} command(s)')

    @tree.command(name="containers", description='list all containers')
    async def containers(interaction: discord.Interaction):
        status_message = StatusMessage('List containers')
        try:
            containers = state.get_containers()
            status_message.add_logs('\n'.join(containers))
            status_message.finish()
        except:
            status_message.fail()
        await interaction.response.send_message(status_message.render())

    @tree.command(name="startall", description='start all containers')
    async def start_all(interaction: discord.Interaction):
        status_message = StatusMessage(f'Start all containers')
        async def hook(log_segment):
            nonlocal status_message
            status_message.add_logs(log_segment)
            await interaction.edit_original_response(content=status_message.render())
        await interaction.response.send_message(status_message.render())

        try:
            await docker.start_all_containers(hook)
            status_message.finish()
        except:
            status_message.fail()
        await interaction.edit_original_response(content=status_message.render())

    @tree.command(name="status", description='get bot status')
    async def status(interaction: discord.Interaction):
        await interaction.response.send_message('#TODO')


    async def container_list_autocompletion(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        data = [app_commands.Choice(name=f'{i}', value=str(i)) for i in state.get_containers() if current.lower() in f'{i}'.lower()]
        return data

    @tree.command(name="update", description='update a container')
    @app_commands.describe(container='Container to update')
    @app_commands.autocomplete(container=container_list_autocompletion)
    async def update(interaction: discord.Interaction, container: str):
        state.stale_containers()
        status_message = StatusMessage(f'Update container {container}')
        await interaction.response.send_message(status_message.render())

        async def hook(log_segment):
            nonlocal status_message
            status_message.add_logs(log_segment)
            await interaction.edit_original_response(content=status_message.render())
        try:
            await docker.update_container(container, hook)
            status_message.finish()
        except:
            status_message.fail()
        await interaction.edit_original_response(content=status_message.render())

    return client

def main():
    client = create_client()
    client.run(environment.discord_token)

if __name__ == '__main__':
    main()

