# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/encryption.py
import json
import base64
from cryptography.hazmat.primitives.serialization import load_der_private_key
from cryptography.hazmat.backends import default_backend
from authlib.jose import JsonWebEncryption

def load_private_key(path_to_key_file):
    with open(path_to_key_file, 'rb') as key_file:
        return load_der_private_key(key_file.read(), password=None, backend=default_backend())

def decrypt_jwe_payload(jwe_payload, private_key):
    jwe = JsonWebEncryption()
    decrypted_data = jwe.deserialize_compact(jwe_payload, private_key)
    if 'payload' in decrypted_data:
        return json.loads(decrypted_data['payload'].decode('utf-8'))
    return None
