# /Users/apichet/Downloads/cheetah-insurance-app/backend/middleware/middleware.py
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import jsonify, request
import logging
from backend.models.Customers import Customers
from backend.models.Admins import Admins  # Import Admin model

# ตั้งค่า Logger
logger = logging.getLogger(__name__)

# ✅ ฟังก์ชันตรวจสอบ Header Authorization
def validate_authorization_header():
    """
    ตรวจสอบการมีอยู่และรูปแบบของ Authorization Header
    """
    auth_header = request.headers.get("Authorization")
    logger.debug(f"🔍 [Authorization] Received Header: {auth_header}")

    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("❌ [Authorization] Missing or Malformed Authorization Header")
        return {"error": "Missing or malformed Authorization header"}, 401
    return None

# ✅ Middleware ตรวจสอบสิทธิ์ของลูกค้า (Customer)
def authorize_customer_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ตรวจสอบ Header
        header_validation = validate_authorization_header()
        if header_validation:
            return jsonify(header_validation[0]), header_validation[1]

        try:
            # ตรวจสอบ JWT Token
            verify_jwt_in_request()
            user_data = get_jwt_identity()
            logger.debug(f"✅ [Customer Access] Token Verified: user_data={user_data}")
        except Exception as e:
            logger.warning(f"❌ [Customer Access] Invalid JWT Token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        # ตรวจสอบ customer_id
        customer_id = kwargs.get("customer_id")
        if not customer_id:
            logger.warning("❌ [Customer Access] Missing customer_id in URL")
            return jsonify({"error": "Missing customer_id"}), 400

        # ตรวจสอบสิทธิ์การเข้าถึง
        customer = Customers.query.filter_by(customer_id=customer_id).first()
        if not customer or not customer.user or customer.user.user_id != user_data.get("user_id"):
            logger.warning(f"❌ [Customer Access] Unauthorized user_id={user_data.get('user_id')}, customer_id={customer_id}")
            return jsonify({"error": "Unauthorized"}), 403

        return f(*args, **kwargs)
    return decorated_function

# ✅ Middleware ตรวจสอบสิทธิ์ของ Admin
def authorize_admin_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ตรวจสอบ Header
        header_validation = validate_authorization_header()
        if header_validation:
            logger.warning(f"🚨 [Admin Access] Authorization Header Failed: {header_validation}")
            return jsonify(header_validation[0]), header_validation[1]

        try:
            # ตรวจสอบ JWT Token
            verify_jwt_in_request()
            user_data = get_jwt_identity()
            logger.debug(f"✅ [Admin Access] Token Verified: user_data={user_data}")

            # ตรวจสอบว่า role เป็น admin หรือ superadmin เท่านั้น
            role = user_data.get("role")
            if role not in ["admin", "superadmin"]:
                logger.warning(f"❌ [Admin Access] Unauthorized user_data={user_data}")
                return jsonify({"error": "Unauthorized. Admin role required."}), 403
        except Exception as e:
            logger.warning(f"❌ [Admin Access] Invalid JWT Token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function

# ✅ Middleware ตรวจสอบสิทธิ์ของ Superadmin
def authorize_superadmin_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ตรวจสอบ Header
        header_validation = validate_authorization_header()
        if header_validation:
            logger.warning(f"🚨 [Superadmin Access] Authorization Header Failed: {header_validation}")
            return jsonify(header_validation[0]), header_validation[1]

        try:
            # ตรวจสอบ JWT Token
            verify_jwt_in_request()
            user_data = get_jwt_identity()
            logger.debug(f"✅ [Superadmin Access] Token Verified: user_data={user_data}")

            # ตรวจสอบว่า role เป็น superadmin เท่านั้น
            if user_data.get("role") != "superadmin":
                logger.warning(f"❌ [Superadmin Access] Unauthorized user_data={user_data}")
                return jsonify({"error": "Unauthorized. Superadmin role required."}), 403
        except Exception as e:
            logger.warning(f"❌ [Superadmin Access] Invalid JWT Token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function