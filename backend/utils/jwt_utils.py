# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/jwt_utils.py
import jwt
import time  # ใช้ time.time() แทน datetime.utcnow().timestamp()
import json
from datetime import datetime, timedelta
import logging
from backend.config.config import Config
from backend.models.Users import Users
from backend.models.Admins import Admins


# ตั้งค่า Logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# อนุญาตความคลาดเคลื่อนของเวลา 5 นาที (300 วินาที)
ALLOWED_TIME_DRIFT = 300

# ตรวจสอบว่า JWT_SECRET_KEY ถูกตั้งค่า
if not Config.JWT_SECRET_KEY:
    logger.error("❌ JWT_SECRET_KEY is not set! Please check your environment variables.")
    raise ValueError("JWT_SECRET_KEY is not configured.")



# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/jwt_utils.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/jwt_utils.py

def generate_jwt(payload, secret=None, expires_in_minutes=None):
    """
    Generate JWT Token โดยตรวจสอบให้ identity เป็น dict เสมอ
    """
    if not payload:
        raise ValueError("Payload cannot be None or empty.")

    secret = secret or Config.JWT_SECRET_KEY

    # ✅ รองรับ config ทั้งแบบเป็นวินาทีและนาที
    raw_exp = Config.JWT_ACCESS_TOKEN_EXPIRES
    expires_in_minutes = expires_in_minutes or (raw_exp if raw_exp <= 120 else raw_exp // 60)

    user_id = payload.get("user_id")
    admin_id = payload.get("admin_id")
    if not user_id and not admin_id:
        raise ValueError("Payload must include 'user_id' or 'admin_id'.")

    identity = {"user_id": user_id, "admin_id": admin_id} if admin_id else {"user_id": user_id}

    now = datetime.utcnow()
    payload.update({
        "identity": identity,
        "sub": str(admin_id) if admin_id else str(user_id),
        "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp()),
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp())
    })

    try:
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token
    except Exception as e:
        raise ValueError(f"Error generating JWT: {e}")





def decode_jwt(token, secret=None, verify_exp=True):
    """
    Decode JWT token และตรวจสอบความถูกต้องของ payload
    """
    secret = secret or Config.JWT_SECRET_KEY

    if not token:
        logger.error("❌ No token provided for decoding.")
        raise ValueError("No token provided")

    try:
        # แสดง token (แต่ truncate เพื่อความปลอดภัย)
        logger.debug(f"🔍 [decode_jwt] Attempting to decode token: {token[:10]}... (truncated)")

        # Decode JWT
        decoded_token = jwt.decode(
            token, 
            secret, 
            algorithms=["HS256"], 
            options={"verify_exp": verify_exp}
        )

        # ✅ แก้ปัญหา: ตรวจสอบว่า decoded_token เป็น JSON string หรือไม่
        if isinstance(decoded_token, str):
            decoded_token = json.loads(decoded_token)

        logger.debug(f"✅ [decode_jwt] Token Decoded Successfully: {decoded_token}")

        # ใช้ time.time() เพื่อดึงค่าเวลาปัจจุบันที่เป็น UNIX timestamp
        now = time.time()
        exp = decoded_token.get("exp")
        iat = decoded_token.get("iat")
        nbf = decoded_token.get("nbf")

        logger.warning(f"📌 [DEBUG] Now: {datetime.utcfromtimestamp(now)}, Allowed Drift: {ALLOWED_TIME_DRIFT}s")

        if exp and exp < now - ALLOWED_TIME_DRIFT:
            logger.warning(f"❌ Token expired at {datetime.utcfromtimestamp(exp)}")
            raise ValueError("Token has expired")

        if iat and iat > now + ALLOWED_TIME_DRIFT:
            logger.warning(f"⚠️ Token issued in the future at {datetime.utcfromtimestamp(iat)}")
            raise ValueError("Token issue time is incorrect")

        if nbf and nbf > now + ALLOWED_TIME_DRIFT:
            logger.warning(f"⚠️ Token not valid before {datetime.utcfromtimestamp(nbf)}")
            raise ValueError("Token is not yet valid")

        # ✅ แก้ปัญหา Missing user_id / admin_id
        user_id = decoded_token.get("user_id")
        admin_id = decoded_token.get("admin_id")

        if not user_id and not admin_id and "sub" in decoded_token:
            if decoded_token.get("role") == "admin":
                admin_id = int(decoded_token["sub"])
            else:
                user_id = int(decoded_token["sub"])

        # ❌ ถ้ายังไม่มี user_id/admin_id อยู่ดี แสดงว่า Token ผิดพลาด
        if not user_id and not admin_id:
            logger.error(f"❌ [decode_jwt] Missing user_id/admin_id in token: {decoded_token}")
            raise ValueError("Invalid token payload: Missing user_id or admin_id")

        # ✅ ตรวจสอบ role
        if "role" not in decoded_token:
            decoded_token["role"] = "admin" if admin_id else "user"

        # ✅ ตรวจสอบ email
        if "email" not in decoded_token:
            user = Admins.query.get(admin_id) if admin_id else Users.query.get(user_id)
            if user:
                decoded_token["email"] = user.email
                logger.info(f"📧 [decode_jwt] Retrieved missing email from DB: {user.email}")
            else:
                logger.error("❌ [decode_jwt] Missing email in token and DB lookup failed")
                raise ValueError("Invalid token payload: Missing email")

        return decoded_token

    except jwt.ExpiredSignatureError:
        logger.warning("❌ Token has expired.")
        raise ValueError("Token has expired")

    except jwt.DecodeError:
        logger.warning("❌ Token decoding failed.")
        raise ValueError("Token decoding failed")

    except jwt.InvalidTokenError as e:
        logger.warning(f"❌ Invalid token: {e}")
        raise ValueError("Invalid token")

    except Exception as e:
        logger.exception(f"❌ Unexpected error while decoding JWT: {e}")
        raise ValueError("An unexpected error occurred while decoding JWT")

def is_token_expired(token, secret=None):
    """
    Check if the token is expired without raising an exception.
    """
    try:
        decode_jwt(token, secret)
        return False
    except ValueError as e:
        if "expired" in str(e).lower():
            return True
        raise
# /Users/apichet/Downloads/cheetah-insurance-app/backend/utils/jwt_utils.py
def generate_refresh_token(user_id=None, admin_id=None, email=None, role=None, secret=None, expires_in_days=7):
    """
    Generate a Refresh JWT token with a longer expiration time.
    """
    secret = secret or Config.JWT_SECRET_KEY
    payload = {}

    logger.debug(f"🔍 [generate_refresh_token] user_id={user_id}, admin_id={admin_id}, email={email}, role={role}")

    # ✅ ถ้าเป็น admin แต่ไม่มี `user_id` ให้กำหนด `user_id = admin_id`
    if admin_id and not user_id:
        user_id = admin_id

    # ✅ ตรวจสอบว่า `user_id` เป็น Integer
    if not isinstance(user_id, int):
        logger.error(f"❌ [generate_refresh_token] Invalid user_id: {user_id} (Expected integer)")
        raise ValueError("Invalid user_id format")

    # ✅ ดึงข้อมูลจาก Database
    user = Admins.query.get(admin_id) if admin_id else Users.query.get(user_id)
    if not user:
        logger.error(f"❌ [generate_refresh_token] User/Admin not found. admin_id={admin_id}, user_id={user_id}")
        raise ValueError("Invalid user or admin credentials.")

    # ✅ ตั้งค่า Email และ Role
    if not email:
        email = user.email
    if not role:
        role = "admin" if admin_id else "user"

    # ✅ **แก้ไขตรงนี้**: ให้ `user_id` มีค่าทุกกรณี
    payload.update({
        "user_id": user_id,  # 🔥 ต้องมี user_id เสมอ
        "admin_id": admin_id if admin_id else None,  # ✅ ถ้าเป็น user ปกติ admin_id จะเป็น None
        "sub": str(user_id),  # ✅ ใช้ user_id เป็น sub
        "role": role,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=expires_in_days),
        "iat": datetime.utcnow(),
        "nbf": datetime.utcnow()
    })

    try:
        logger.debug(f"🔍 [generate_refresh_token] Payload before encoding: {payload}")
        token = jwt.encode(payload, secret, algorithm="HS256")
        logger.debug(f"✅ [generate_refresh_token] Token Generated Successfully")
        return token
    except Exception as e:
        logger.error(f"❌ [generate_refresh_token] Error generating Refresh JWT: {e}")
        raise ValueError(f"Error generating Refresh JWT: {e}")
