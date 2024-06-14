from rsa import PublicKey, PrivateKey


class UserManager:
    def __init__(self, owner: str = None):
        self._data = {}
        self._owner = owner

    def add_user(self, username: str, public_key: PublicKey, private_key: PrivateKey = None):
        self._data[username] = (public_key, private_key)

    def set_owner(self, username: str):
        self._owner = username

    def get_public_key(self, username: str):
        return self._data.get(username, [None, None])[0]

    def get_private_key(self, username: str):
        return self._data.get(username, [None, None])[1]

    def get_opponent(self):
        return [x for x in self._data if x != self._owner][0]

    def get_owner(self):
        assert self._owner is not None, "No owner specified"
        return self._owner


__all__ = [
    'UserManager',
]