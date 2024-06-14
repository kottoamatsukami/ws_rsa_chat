from websocket import WebSocketApp, WebSocket
from core import *
import datetime
import json
import rsa

try:
    import thread
except ImportError:
    import _thread as thread

SERVER_WS_ENDPOINT = 'ws://127.0.0.1:8000/ws'
USER_MANAGER       = UserManager()
EXIT_COMMAND       = '/q'


def on_open(ws: WebSocketApp):
    # Send auth package
    ws.send_text(USER_MANAGER.get_owner())
    ws.send_bytes(
        USER_MANAGER.get_public_key(
            USER_MANAGER.get_owner()
        ).save_pkcs1()
    )

    # Run non-blocking input in the additional thread
    def run():
        while True:
            message = input('')

            # Command for quit
            if message == EXIT_COMMAND:
                ws.close()
                break

            # Encrypt and send message
            pkey = USER_MANAGER.get_public_key(USER_MANAGER.get_opponent())
            if pkey is not None:
                message = f"[{datetime.datetime.now()}]<{USER_MANAGER.get_owner()}>: {message}".encode('utf-8')
                status, result = encode_message(message, pkey)
                if status:
                    ws.send_bytes(result)
                else:
                    error("Your message to long. Please, increase bits of key or make message shorter.")
            else:
                print('[HINT]: There is only you in the room')

    thread.start_new_thread(run, ())


def on_message(_: WebSocket, message: str):
    def msg_handle(msg):
        package = json.loads(msg)
        # Normal package condition
        if 'type' in package:

            # handle <key_exchange> package
            if package['type'] == 'key_exchange':
                opponent_address  = package['owner']
                pkey              = rsa.PublicKey.load_pkcs1(bytes(package['pkey'], encoding='utf8'))
                USER_MANAGER.add_user(opponent_address, pkey)
                print('[CLIENT] Key Exchange Successfully')

            # handle <message> package
            elif package['type'] == 'message':
                if package['extra'] == 'info':
                    print(package['message'])
                else:
                    status, msg = extract_bytes_from_str(package['message'])
                    pkey        = USER_MANAGER.get_public_key(package['sender'])
                    if status:
                        success, msg = decode_message(
                            msg,
                            USER_MANAGER.get_private_key(
                                USER_MANAGER.get_owner()
                            )) if pkey is not None else (False, msg)
                        if success:
                            print(msg.decode('utf-8'))

            # handle <disconnect> package
            elif package['type'] == 'disconnect':
                print('[CLIENT] user disconnected')

    thread.start_new_thread(msg_handle, (message,))


def on_close(_: WebSocket, *args):
    print('Connection closed')


def main():
    # Get user parameters
    room = input('Enter room name: ')
    name = input('Enter your name: ')

    # load rsa keys
    public_key, private_key = handle_keypair(name)

    # Set extra info for manager
    USER_MANAGER.set_owner(name)
    USER_MANAGER.add_user(name, public_key, private_key)

    # Initialize WebSocketApp
    wsc = WebSocketApp(SERVER_WS_ENDPOINT + '/' + room, on_close=on_close)
    wsc.on_close   = on_close
    wsc.on_message = on_message
    wsc.on_open    = on_open

    # Run client
    wsc.run_forever()


if __name__ == '__main__':
    main()