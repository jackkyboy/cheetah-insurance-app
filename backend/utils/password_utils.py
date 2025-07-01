# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/password_utils.py
import hashlib
import binascii
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def hash_password(password):
    """
    Hash a password using scrypt algorithm.
    """
    salt = hashlib.sha256(password.encode()).digest()[:16]
    derived_key = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=8192,  # ✅ ลดจาก 32768 → 8192 หรือ 4096 ถ้ายังเกิดปัญหา
        r=8,
        p=1,
        dklen=64
    )
    hashed_password = f"scrypt:8192:8:1${binascii.hexlify(salt).decode()}${binascii.hexlify(derived_key).decode()}"

    logger.debug(f"🔐 Hashed Password: {hashed_password}")
    return hashed_password

def verify_scrypt_password(stored_password, provided_password):
    """
    Verify a stored scrypt password hash against a provided password.
    """
    try:
        logger.debug(f"🔍 Verifying password for stored hash: {stored_password}")

        parts = stored_password.split('$')
        if len(parts) != 3:
            logger.error(f"❌ Invalid stored password format: {stored_password}")
            return False

        n, r, p = map(int, parts[0].split(":")[1:])
        salt = binascii.unhexlify(parts[1])
        stored_hash = binascii.unhexlify(parts[2])

        derived_key = hashlib.scrypt(
            provided_password.encode('utf-8'),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(stored_hash)
        )

        is_match = stored_hash == derived_key
        logger.debug(f"✅ Password Match: {is_match}")
        return is_match
    except Exception as e:
        logger.error(f"❌ Password verification failed: {e}")
        return False
