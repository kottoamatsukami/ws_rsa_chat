# WSRSA Chat
This project is a simple WebSocket chat using RSA encryption for secure data transfer.

## Installing
```bash
git clone https://github.com/kottoamatsukami/ws_rsa_chat.git
cd ws_rsa_chat
```
Make sure you have Poetry installed (https://python-poetry.org). Then run the following commands:
```bash
poetry install
```
For deploy server use:
```bash
poetry run fastapi run server.py
```
To use client use:
```bash
poetry run python client.py
```

Also, you can run some tests with:
```bash
poetry run pytest
```
