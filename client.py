from websocket import WebSocketApp, WebSocket
from core.utils import *
from pathlib import Path
import datetime
import json
import rsa

try:
    import thread
except ImportError:
    import _thread as thread

# HYPERPARAMS
SERVER_WS_ENDPOINT = 'ws://127.0.0.1:8000/ws'
KEYPAIR_PATH       = './keys'
KEY_BITS           = 1024


if __name__ == '__main__':
    pkey = None

    # Get user parameters
    room = input('Enter room name: ')
    name = input('Enter your name: ')

    # Generate or load RSA keys
    public_key_path  = Path(KEYPAIR_PATH) / name / 'public.pem'
    private_key_path = Path(KEYPAIR_PATH) / name / 'private.pem'

    if public_key_path.exists() and private_key_path.exists():
        # Load RSA keypair
        with open(public_key_path, 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open(private_key_path, 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())

    else:
        # Generate RSA keypair
        (public_key, private_key) = rsa.newkeys(KEY_BITS)
        (Path(KEYPAIR_PATH) / name).mkdir(parents=True)

        # Save keypair in cache
        with open(public_key_path, 'wb') as f:
            f.write(public_key.save_pkcs1())
        with open(private_key_path, 'wb') as f:
            f.write(private_key.save_pkcs1())

    #
    # WebSocket's event handlers definition
    #
    def on_open(ws: WebSocketApp):
        """
        This function is called when the websocket is open.
        :param ws: WebSocketApp
        :return: None
        """

        # Send auth package
        ws.send_text(name)
        ws.send_bytes(public_key.save_pkcs1())

        # Run non-blocking input in the additional thread
        def run():
            while True:
                message = input('')

                # Command for quit
                if message == '/q':
                    ws.close()
                    break

                # Encrypt and send message
                if pkey is not None:
                    message = f"[{datetime.datetime.now()}]<{name}>: {message}".encode('utf-8')
                    status, result = encode_message(message, pkey)
                    if status:
                        ws.send_bytes(result)
                    else:
                        error("Your message to long. Please, increase bits of key or make message shorter.")
                else:
                    print('[HINT]: There is only you in the room')

        thread.start_new_thread(run, ())


    def on_message(_: WebSocket, message: str):
        """
        This function is called when the websocket is open.
        :param _:       WebSocketApp (not used)
        :param message: str
        :return: None
        """
        def msg_handle(msg):
            global pkey
            package = json.loads(msg)

            # Normal package condition
            if 'type' in package:

                # handle <key_exchange> package
                if package['type'] == 'key_exchange':
                    key_b = bytes(package['pkey'], encoding='utf8')
                    pkey = rsa.PublicKey.load_pkcs1(key_b)
                    print('[CLIENT] Key Exchange Successfully')

                # handle <message> package
                elif package['type'] == 'message':
                    if package['extra'] == 'info':
                        print(package['message'])
                    else:
                        status, msg = extract_bytes_from_str(package['message'])
                        if status:
                            success, msg = decode_message(msg, private_key) if pkey is not None else (False, msg)
                            if success:
                                print(msg.decode('utf-8'))

                # handle <disconnect> package
                elif package['type'] == 'disconnect':
                    print('[CLIENT] user disconnected')
                    pkey = None

        thread.start_new_thread(msg_handle, (message, ))

    def on_close(_: WebSocket, *args):
        print('Connection closed')
    #
    # Initialize WebSocketApp
    #
    wsc = WebSocketApp(SERVER_WS_ENDPOINT + '/' + room, on_close=on_close)
    wsc.on_message = on_message
    wsc.on_open    = on_open

    # Run client
    wsc.run_forever()
