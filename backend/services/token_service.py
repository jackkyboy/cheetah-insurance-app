# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/token_service.py
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backend.config.config import Config  # Import Config อย่างถูกต้อง

# โหลด Environment Variables
load_dotenv()

# ตั้งค่าจาก Config
SECRET_KEY = Config.JWT_SECRET_KEY
JWT_ACCESS_EXPIRY_MINUTES = Config.JWT_ACCESS_TOKEN_EXPIRES // 60  # ค่าใน Config เป็นวินาที ต้องแปลงเป็นนาที
JWT_REFRESH_EXPIRY_DAYS = Config.JWT_REFRESH_TOKEN_EXPIRES // 86400  # ค่าใน Config เป็นวินาที ต้องแปลงเป็นวัน

# ฟังก์ชันสำหรับสร้าง Token
def generate_token(data, expiration_minutes=JWT_ACCESS_EXPIRY_MINUTES):
    """
    Generate a JWT token.

    Args:
        data (dict): Data to be encoded in the token.
        expiration_minutes (int): Expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    payload = {
        "data": data,
        "exp": datetime.utcnow() + timedelta(minutes=expiration_minutes),
        "iat": datetime.utcnow(),  # Token issued time
        "nbf": datetime.utcnow()   # Not before (token valid immediately)
    }
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token
    except Exception as e:
        raise Exception(f"Error generating token: {e}")

# ฟังก์ชันสำหรับสร้าง Refresh Token
def refresh_access_token(refresh_token):
    """
    Refresh access token using the given refresh token.
    """
    try:
        payload = verify_token(refresh_token)
        print(f"🔍 Refresh Token ถูกต้อง! Payload: {payload}")

        if "email" not in payload:
            raise ValueError("Refresh Token ไม่มี email!")

        new_access_token = generate_token({
            "user_id": payload["user_id"],
            "email": payload["email"],
            "role": payload["role"]
        })
        return new_access_token
    except Exception as e:
        raise Exception(f"Error refreshing access token: {e}")



# ฟังก์ชันสำหรับตรวจสอบ Token
def verify_token(token):
    """
    Verify a JWT token.

    Args:
        token (str): The token to verify.

    Returns:
        dict: Decoded data if the token is valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("data")
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except Exception as e:
        raise Exception(f"Error verifying token: {e}")

# ฟังก์ชันสำหรับสร้าง Token สำหรับ Admin
def verify_admin_token(token):
    """
    Verify an admin token.
    """
    try:
        data = verify_token(token)
        if not data.get("admin_id") or not data.get("role"):
            raise ValueError("Invalid admin token structure")
        
        print(f"🔍 ตรวจสอบ Token: {data}")  # Debug Data ใน Token
        return data
    except Exception as e:
        raise Exception(f"Admin token verification failed: {e}")


# ฟังก์ชันสำหรับตรวจสอบ Token ของ Admin
def verify_admin_token(token):
    """
    Verify an admin token.

    Args:
        token (str): The token to verify.

    Returns:
        dict: Admin data if the token is valid.
    """
    try:
        data = verify_token(token)
        if not data.get("admin_id") or not data.get("role"):
            raise ValueError("Invalid admin token structure")
        return data
    except Exception as e:
        raise Exception(f"Admin token verification failed: {e}")

# ฟังก์ชันสำหรับสร้าง Token สำหรับ User
def generate_user_token(user):
    """
    Generate a JWT token specifically for user accounts.

    Args:
        user (object): User object containing user details.

    Returns:
        str: Encoded JWT token.
    """
    data = {
        "user_id": user.user_id,
        "email": user.email,
        "role": "user"
    }
    return generate_token(data)

# ฟังก์ชันสำหรับตรวจสอบ Token ของ User
def verify_user_token(token):
    """
    Verify a user token.

    Args:
        token (str): The token to verify.

    Returns:
        dict: User data if the token is valid.
    """
    try:
        data = verify_token(token)
        if not data.get("user_id") or data.get("role") != "user":
            raise ValueError("Invalid user token structure")
        return data
    except Exception as e:
        raise Exception(f"User token verification failed: {e}")
