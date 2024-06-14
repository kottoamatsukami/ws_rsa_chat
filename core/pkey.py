from pathlib import Path
import rsa

KEYPAIR_PATH       = './keys'
KEY_BITS           = 1024


def handle_keypair(user_name: str):
    public_key_path  = Path(KEYPAIR_PATH) / user_name / "public.pem"
    private_key_path = Path(KEYPAIR_PATH) / user_name / "private.pem"

    if public_key_path.exists() and private_key_path.exists():
        with open(Path(KEYPAIR_PATH) / user_name / "public.pem", 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
        with open(Path(KEYPAIR_PATH) / user_name / "private.pem", 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
    else:
        (public_key, private_key) = rsa.newkeys(KEY_BITS)
        (Path(KEYPAIR_PATH) / user_name).mkdir(parents=True)

        with open(public_key_path, 'wb') as f:
            f.write(public_key.save_pkcs1())
        with open(private_key_path, 'wb') as f:
            f.write(private_key.save_pkcs1())

    return public_key, private_key


__all__ = [
    'handle_keypair'
]