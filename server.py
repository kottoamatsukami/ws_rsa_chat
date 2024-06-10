import starlette.websockets
import websockets
import asyncio
import json

from starlette.websockets import WebSocket
from fastapi              import FastAPI


pairs = {}

server = FastAPI()


async def disconnect(room, client):
    """
    This function will disconnect the websocket from the client
    :param room:
    :param client:
    :return: None
    """
    if client in pairs[room]:
        try:
            await pairs[room][client]['ws'].close()
        except RuntimeError:
            pass

        del pairs[room][client]

        if len(pairs[room]) == 0:
            del pairs[room]

        for address in pairs[room]:
            await pairs[room][address]['ws'].send_bytes(
                    json.dumps(
                        {
                            'type'   : 'disconnect',
                            'who'    : client,
                        }
                    ).encode('utf-8')
                )


async def send_messages_to_subscribers(message: str, room: str, exclude: set[str], extra: str = ''):
    """
    This function will send messages to the subscribers
    :param message:
    :param room:
    :param exclude:
    :param extra:
    :return:
    """
    disconnected = []
    for sub_address in pairs[room]:
        if sub_address not in exclude:
            try:
                await pairs[room][sub_address]['ws'].send_bytes(
                    json.dumps(
                        {
                            'type'   : 'message',
                            'message': message,
                            'extra'  : extra
                        }
                    ).encode('utf-8')
                )
            except RuntimeError:
                disconnected.append(sub_address)
    for dis in disconnected:
        await disconnect(room, dis)


@server.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    """
    This is the main websocket endpoint
    :param websocket:
    :param room:
    :return:
    """
    await websocket.accept()

    # Receive auth package
    client_name    = await websocket.receive_text()
    client_pkey    = (await websocket.receive_bytes()).decode('utf-8')
    client_address = websocket.client.host + ':' + str(websocket.client.port)

    # Create room
    if room not in pairs:
        pairs[room] = {}

    # Append client to room
    if len(pairs[room]) < 2:
        pairs[room][client_address] = {
            'ws'   : websocket,
            'name' : client_name,
            'pkey' : client_pkey,
        }
    # If the room is full the client just will be disconnected
    else:
        await websocket.close()
        return

    # Send info message
    await send_messages_to_subscribers(
        f"[Server] {client_name} joined the room",
        room, set(), extra='info'
    )

    # Room is full. Exchanging pubkey
    if len(pairs[room]) == 2:
        await send_messages_to_subscribers(
            f"[Server] Room is full",
            room, set(), extra='info'
        )

        other_address = set(pairs[room].keys()).difference({client_address}).pop()

        # Server -> Client : Other.pubkey
        await pairs[room][client_address]['ws'].send_bytes(json.dumps(
            {
                'type': 'key_exchange',
                'pkey':  pairs[room][other_address]['pkey'],
            }
        ))
        # Server -> Other  : Client.pubkey
        await pairs[room][other_address]['ws'].send_bytes(json.dumps(
            {
                'type': 'key_exchange',
                'pkey': pairs[room][client_address]['pkey'],
            }
        ))

    try:
        # Main cycle
        while True:

            if len(pairs[room]) == 2:
                # Some client send message in room
                message = await websocket.receive_bytes()
                # Sending this message to other clients
                await send_messages_to_subscribers(str(message), room, {client_address})

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosedOK:
        pass
    except starlette.websockets.WebSocketDisconnect:
        pass
