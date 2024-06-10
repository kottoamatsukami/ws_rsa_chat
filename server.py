import json

from starlette.websockets import WebSocket
from fastapi              import FastAPI


import starlette.websockets
import websockets
import pprint

pairs = {}

server = FastAPI()


async def disconnect(websocket, client_address, room):
    # Пользователь решил отключиться, удаляем его из комнаты
    del pairs[room][client_address]
    await websocket.close()
    # Чтобы не копить пустые комнаты, удаляем те, в которых нет клиентов
    if len(pairs[room]) == 0:
        del pairs[room]


async def send_messages_to_subscribers(message: str, room: str, exclude: set[str], extra: str = ''):
    for sub_address in pairs[room]:
        if sub_address not in exclude:
            await pairs[room][sub_address]['ws'].send_bytes(json.dumps(
                {
                    'type'   : 'message',
                    'message': message,
                    'extra'  : extra
                }
            )
        )


@server.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    # Подключаем клиента
    await websocket.accept()

    # Получаем пакет авторизации
    client_name    = await websocket.receive_text()
    client_pkey    = (await websocket.receive_bytes()).decode('utf-8')
    client_address = websocket.client.host + ':' + str(websocket.client.port)

    # Создаём парную комнату
    if room not in pairs:
        pairs[room] = {}
    if len(pairs[room]) <= 2:
        pairs[room][client_address] = {'ws': websocket, 'name': client_name, 'pkey': client_pkey}
    if len(pairs[room]) == 2:
        # Обмениваемся публичными ключами
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

    # Оповещаем пользователей комнаты о новом участнике
    await send_messages_to_subscribers(
        f"[Server] Meet [{client_name}] in the room.",
        room,
        {client_address},
        extra='info'
    )
    try:
        # Цикл, отвечающий за ожидание, пока в комнате не станет два человека
        while True:
            pprint.pp(pairs)
            if len(pairs[room]) == 2:
                # Некоторый пользователь отправил сообщение в канал
                message = await websocket.receive_bytes()
                # Рассылаем всем участникам канала
                await send_messages_to_subscribers(str(message), room, {client_address})

            else:
                # Пользователь отправил сообщение в пустую комнату
                await websocket.receive_bytes()
                # Отправим ему сообщение об этом
                if len(pairs[room]) != 2:
                    await send_messages_to_subscribers(
                        "[SERVER] Error: There is only person in room",
                        room, set(), extra='info'
                    )

    except websockets.exceptions.ConnectionClosedOK:
        await disconnect(websocket, client_address, room)
    except starlette.websockets.WebSocketDisconnect:
        await disconnect(websocket, client_address, room)
