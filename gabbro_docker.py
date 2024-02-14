import fabric
import environment

import logging
logger = logging.getLogger(__name__)


def connection():
    return fabric.Connection(
            host=environment.docker_host,
            user=environment.docker_user,
            connect_kwargs={'password': environment.docker_password})

def get_containers():
    with connection() as conn:
        result = conn.run('docker ps --format \'{{.Names}}\'', hide=True, warn=True, pty=False)
        return result.stdout.strip().split('\n')

async def run(conn, hook, command):
    logger.info(f'Running command: `{command}`')
    await hook(f'Running command: `{command}`...\n')
    result = conn.run(command, hide=True, warn=True, pty=False)
    logger.info(f'Command `{command}` stdout:\n{result.stdout}')
    logger.info(f'Command `{command}` stderr:\n{result.stderr}')
    if result.exited != 0:
        await hook(result.stdout or result.stderr)
        raise Exception('Failed to execute correctly')

async def get_container_version(container: str):
    with connection() as conn:
        result = conn.run('docker inspect --format \'{{ index .Config.Labels "org.opencontainers.image.version"}}\' ' + container, hide=True, warn=True, pty=False)
        version = result.stdout.strip().split('\n')[0]
        if version is None or len(version) == 0:
            raise Exception('Container does not have version label')
        return version

async def start_all_containers(hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose start')

async def up_all_containers(hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose up -d')

async def stop_all_containers(hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose stop')

async def down_all_containers(hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose down')

async def start_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose start {container_name}')

async def stop_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose stop {container_name}')

async def up_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose up -d {container_name}')

async def down_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose down {container_name}')

async def update_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose pull {container_name}')
            await run(conn, hook, f'docker compose up -d --force-recreate --build {container_name}')
        await run(conn, hook, f'docker image prune -af')

async def recreate_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose up -d --force-recreate --build {container_name}')
