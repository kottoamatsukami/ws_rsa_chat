import datetime

import websocket
from websocket import WebSocketApp, WebSocket
from pathlib import Path
import pickle
import json
import rsa
import ast


try:
    import thread
except ImportError:
    import _thread as thread

# HYPERPARAMS
SERVER_WS_ENDPOINT = 'ws://127.0.0.1:8000/ws'
KEYPAIR_PATH       = './keys'
KEY_BITS           = 1024


if __name__ == '__main__':
    # room = input('Enter room name: ')
    room                = 'test'
    name                = input('Enter your name: ')
    pkey: rsa.PublicKey = None

    # Генерируем или подгружаем ключи
    public_key_path  = Path(KEYPAIR_PATH) / name / 'public.pem'
    private_key_path = Path(KEYPAIR_PATH) / name / 'private.pem'
    if public_key_path.exists() and private_key_path.exists():
        # Подгружаем
        with open(public_key_path, 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open(private_key_path, 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
    else:
        # Генерируем
        (public_key, private_key) = rsa.newkeys(KEY_BITS)
        (Path(KEYPAIR_PATH) / name).mkdir(parents=True)
        # Сохраняем
        with open(public_key_path, 'wb') as f:
            f.write(public_key.save_pkcs1())
        with open(private_key_path, 'wb') as f:
            f.write(private_key.save_pkcs1())

    # Добавим обработчиков событий
    def on_open(ws: WebSocketApp):
        # Информируем об успехе
        print('Connection established')

        # Отправляем пакет авторизации
        ws.send_text(name)
        ws.send_bytes(public_key.save_pkcs1())

        # Запускаем неблокирующую консоль
        def run():
            while True:
                message = input('')

                if message == '/q':
                    ws.close()
                    break

                if pkey is not None:
                    message = f"[{datetime.datetime.now()}]<{name}>: {message}"
                    message = rsa.encrypt(message.encode('utf-8'), pkey)

                ws.send_bytes(message)
        thread.start_new_thread(run, ())


    def on_message(_: WebSocket, message):
        def msg_handle(msg):
            global pkey
            package = json.loads(msg)
            if 'type' in message:
                if package['type'] == 'key_exchange':
                    key_b = bytes(package['pkey'], encoding='utf8')
                    pkey = rsa.PublicKey.load_pkcs1(key_b)
                    print('Key Exchange Successfully')
                elif package['type'] == 'message':
                    if package['extra'] == 'info':
                        print(package['message'])
                    else:
                        msg = ast.literal_eval(package['message'])
                        if pkey is not None:
                            msg = rsa.decrypt(msg, private_key).decode('utf-8')
                        print(msg)

        thread.start_new_thread(msg_handle, (message, ))


    wsc = WebSocketApp(SERVER_WS_ENDPOINT + '/' + room)
    wsc.on_message = on_message
    wsc.on_close   = lambda _: print('Connection closed')
    wsc.on_open    = on_open

    wsc.run_forever()
