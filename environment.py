import os
def get_env(key):
    value = os.getenv(key)
    if value is None:
        raise Exception(f'Missing environment variable {key}')
    return value

discord_token = get_env('COM_GABBRO_DISCORD_TOKEN')

docker_host = get_env('COM_GABBRO_DOCKER_HOST')
docker_user = get_env('COM_GABBRO_DOCKER_USER')
docker_password = get_env('COM_GABBRO_DOCKER_PASSWORD')
docker_path = get_env('COM_GABBRO_DOCKER_PATH')
