import fabric
import environment


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
    await hook(f'Running command: `{command}`...\n')
    result = conn.run(command, hide=True, warn=True, pty=False)
    if result.exited != 0:
        await hook(result.stdout or result.stderr)
        raise Exception('Failed to execute correctly')

async def update_container(container_name, hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose pull {container_name}')
            await run(conn, hook, f'docker compose up -d --force-recreate --build {container_name}')
        await run(conn, hook, f'docker image prune -af')

async def start_all_containers(hook):
    with connection() as conn:
        with conn.cd(environment.docker_path):
            await run(conn, hook, f'docker compose up -d')
