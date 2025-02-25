from asyncua import Client

from palopcua import config


async def get_client() -> Client:
    """
    Returns the client

    Returns:
        Client: open client
    """

    url = f"opc.tcp://{config.OPCUA_CLIENT_SERVER_NAME}:{config.OPCUA_CLIENT_SERVER_PORT}"

    client = Client(url=url, timeout=1)

    if config.OPCUA_CLIENT_USER:
        client.set_user(config.OPCUA_CLIENT_USER)
    if config.OPCUA_CLIENT_PASSWORD:
        client.set_password(config.OPCUA_CLIENT_PASSWORD)

    await client.connect()

    return client
