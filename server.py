import starlette.websockets
import websockets
import asyncio
import json

from starlette.websockets import WebSocket
from fastapi              import FastAPI


pairs = {}

server = FastAPI()

MAX_CLIENTS_IN_ROOM = 2


async def disconnect(room: str, client):
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


async def send_messages_to_subscribers(sender: str, message: str, room: str, exclude: set[str], extra: str = ''):
    disconnected = []
    for sub_address in pairs[room]:
        if sub_address in exclude:
            continue
        try:
            await pairs[room][sub_address]['ws'].send_bytes(
                json.dumps(
                    {
                        'type'   : 'message',
                        'message': message,
                        'sender' : sender,
                        'extra'  : extra
                    }
                ).encode('utf-8')
            )
        except RuntimeError:
            disconnected.append(sub_address)
    for dis in disconnected:
        await disconnect(room, dis)


async def exchange_keys(room, client_address):
    await send_messages_to_subscribers(
        "Server", f"[Server] Room is full",
        room, set(), extra='info'
    )

    other_address = set(pairs[room].keys()).difference({client_address}).pop()

    # Server -> Client : Other.pubkey
    await pairs[room][client_address]['ws'].send_bytes(json.dumps(
        {
            'type': 'key_exchange',
            'pkey': pairs[room][other_address]['pkey'],
            'owner': other_address,
        }
    ))
    # Server -> Other  : Client.pubkey
    await pairs[room][other_address]['ws'].send_bytes(json.dumps(
        {
            'type': 'key_exchange',
            'pkey': pairs[room][client_address]['pkey'],
            'owner': client_address,
        }
    ))


async def exchange_cycle(room: str, websocket: WebSocket, client_address: str, client_name: str):
    try:
        # Main cycle
        while True:

            if len(pairs[room]) == 2:
                # Some client send message in room
                message = await websocket.receive_bytes()
                # Sending this message to other clients
                await send_messages_to_subscribers(client_address, str(message), room, {client_address})

            await asyncio.sleep(1)

    except websockets.exceptions.ConnectionClosedOK:
        pass
    except starlette.websockets.WebSocketDisconnect:
        pass


@server.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()

    # Receive auth package
    client_name    = await websocket.receive_text()
    client_pkey    = (await websocket.receive_bytes()).decode('utf-8')
    client_address = websocket.client.host + ':' + str(websocket.client.port)

    # Create room
    if room not in pairs:
        pairs[room] = {}

    # Append client to room
    if len(pairs[room]) < MAX_CLIENTS_IN_ROOM:
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
        "Server", f"[Server] {client_name} joined the room",
        room, set(), extra='info'
    )

    # Room is full. Exchanging pubkey
    if len(pairs[room]) == 2:
        await exchange_keys(room, client_address)

    # Run message exchanging
    await exchange_cycle(room, websocket, client_address, client_name)
