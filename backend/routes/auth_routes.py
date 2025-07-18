# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/auth_routes.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from backend.config.config import Config  # ✅ เพิ่ม Config
from backend.models.Admins import Admins
from backend.models.Users import Users
from backend.models import db
from backend.models.Customers import Customers
from backend.utils.password_utils import verify_scrypt_password
from backend.utils.jwt_utils import generate_jwt, decode_jwt, generate_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash  # ✅ IMPORT check_password_hash
from datetime import datetime, timedelta  # ✅ ใช้ datetime ได้ถูกต้อง
import jwt
import logging
import datetime
from flask_mail import Message

# ✅ ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ✅ กำหนด Blueprint สำหรับ auth routes
auth_bp = Blueprint("auth", __name__)



# ✅ Helper Function: Generate Access Token
def generate_access_token(user_id, email, role, secret=None, expires_in_minutes=None):
    """
    Generate an access JWT token.

    Args:
        user_id (int): ID ของผู้ใช้
        email (str): Email ของผู้ใช้
        role (str): บทบาทของผู้ใช้ (admin หรือ user)
        secret (str, optional): Secret key สำหรับ JWT (default: Config.JWT_SECRET_KEY)
        expires_in_minutes (int, optional): เวลาหมดอายุของ token (default: Config.JWT_ACCESS_TOKEN_EXPIRES)

    Returns:
        str: JWT access token
    """
    if not user_id:
        raise ValueError("User ID is required for generating access token.")
    if not email:
        raise ValueError("Email is required for generating access token.")
    if not role:
        raise ValueError("Role is required for generating access token.")

    # ✅ ใช้ default ถ้าไม่ได้ส่ง expires_in_minutes มา
    token_expiry = expires_in_minutes or Config.JWT_ACCESS_TOKEN_EXPIRES

    return generate_jwt(
        {
            "user_id": user_id,
            "email": email,
            "role": role
        },
        secret=secret or Config.JWT_SECRET_KEY,
        expires_in_minutes=token_expiry
    )




# ✅ Route: Register
# ✅ Route: Register
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        logger.info(f"📥 Register request received: {data}")

        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        # 🧪 Validate fields
        if not all([email, password, first_name, last_name]):
            logger.warning("⚠️ Missing required fields.")
            return jsonify({"error": "All fields are required"}), 400

        # 🔍 Check if customer exists
        existing_customer = Customers.find_by_email(email)
        if existing_customer:
            logger.warning(f"⚠️ Email already exists: {email}")
            return jsonify({"error": "Email already registered"}), 400

        # 🔐 Create new user first
        new_user = Users(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # 🧬 ดึง user_id มาใช้

        # 👤 Create customer with user_id
        new_customer = Customers(
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_id=new_user.user_id  # ✅ ใส่ FK ไปยัง Users
        )
        db.session.add(new_customer)

        db.session.commit()
        logger.info(f"✅ User registered: {email} (user_id={new_user.user_id})")
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Registration failed: {str(e)}", exc_info=True)
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


    

# ✅ Route: Login (Admin & User)
# ✅ Route: Login (Admin & User)
# ✅ Route: Login (Admin & User)
# ✅ Route: Login (Admin & User)
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "").strip()

        logger.info(f"🔍 [Backend] Login attempt for: {email}")

        if not email or not password:
            logger.warning("❌ Missing email or password")
            return jsonify({"error": "Email and password are required"}), 400

        # ✅ เช็คว่า Flask App ถูกต้องก่อนใช้ SQLAlchemy
        if not current_app or not db:
            logger.error("❌ current_app หรือ db ไม่พร้อมใช้งาน")
            return jsonify({"error": "Database connection error"}), 500

        # ✅ ใช้ current_app.app_context() เพื่อตรวจสอบว่ามีการเชื่อม DB จริงๆ
        with current_app.app_context():
            logger.debug(f"🔎 Checking database connection before querying...")
            logger.debug(f"🔍 Database URI: {current_app.config.get('SQLALCHEMY_DATABASE_URI')}")

            try:
                # ✅ ตรวจสอบ Admin ก่อน
                admin = Admins.query.filter_by(email=email).first()

                # ✅ ถ้าไม่เจอใน Admin, ตรวจสอบใน Users
                user = Users.query.filter_by(email=email).first()

                if admin:
                    if not admin.check_password(password):
                        logger.warning("❌ Invalid password for Admin")
                        return jsonify({"error": "Invalid email or password"}), 401

                    role = "admin"
                    user_id = admin.admin_id

                elif user:
                    if not user.check_password(password):
                        logger.warning("❌ Invalid password for User")
                        return jsonify({"error": "Invalid email or password"}), 401

                    role = "user"
                    user_id = user.user_id

                else:
                    logger.warning(f"❌ No user found with email: {email}")
                    return jsonify({"error": "Invalid email or password"}), 401

                # ✅ สร้าง Access Token และ Refresh Token
                access_token = generate_access_token(user_id=user_id, email=email, role=role)
                refresh_token = generate_refresh_token(user_id=user_id, email=email, role=role)

                logger.info(f"✅ {role.capitalize()} {email} logged in successfully")

                return jsonify({
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "user_id": user_id,
                        "email": email,
                        "role": role
                    }
                }), 200

            except Exception as db_error:
                logger.error(f"❌ Database Query Failed: {db_error}", exc_info=True)
                return jsonify({"error": "Database query failed"}), 500

    except Exception as e:
        logger.error(f"❌ Unexpected error during login: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500



# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/auth_routes.py
# ✅ Route: Refresh Token
@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    try:
        logger.info("🔄 [REQUEST] Received refresh token request")

        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400

        logger.debug(f"🔍 Decoding refresh token: {refresh_token[:30]}... (truncated)")

        try:
            payload = decode_jwt(refresh_token)
            if isinstance(payload, str):  # ตรวจสอบว่า payload เป็น string หรือไม่
                import json
                payload = json.loads(payload)
        except ValueError as e:
            logger.warning(f"❌ [Refresh] Token verification failed: {str(e)}")
            return jsonify({"error": str(e)}), 401

        # ✅ แก้ไขตรงนี้ให้รองรับทั้ง User และ Admin
        user_id = payload.get("user_id") or payload.get("admin_id")  
        email, role = payload.get("email"), payload.get("role")

        if not user_id or not email or not role:
            logger.error("❌ [Refresh] Invalid token payload (missing required fields)")
            return jsonify({"error": "Invalid refresh token"}), 401

        logger.info(f"✅ [Refresh] Token valid for user_id={user_id}, email={email}, role={role}")

        # ✅ สร้าง Access Token และ Refresh Token ใหม่
        new_access_token = generate_access_token(user_id, email, role)
        new_refresh_token = generate_refresh_token(user_id, email=email, role=role)

        logger.info(f"✅ [Refresh] New tokens generated for {email}")
        return jsonify({
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }), 200

    except Exception as e:
        logger.error(f"❌ [Refresh] Unexpected server error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected server error occurred"}), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    data = request.get_json()
    user_id = data.get("user_id")
    role = data.get("role")  # ✅ เพิ่ม role

    if role == "admin":
        user = Admins.query.filter_by(admin_id=user_id).first()
    else:
        user = Users.query.filter_by(user_id=user_id).first()

    if user:
        user.refresh_token = None  # ลบ Refresh Token ออกจากระบบ
        db.session.commit()
        return jsonify({"message": "Logged out successfully"}), 200

    return jsonify({"error": "User not found"}), 404





# ✅ Route: Forgot Password
# ✅ Route: Forgot Password
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # ค้นหาผู้ใช้ในตาราง Users หรือ Admins
        user = Users.query.filter_by(email=email).first() or Admins.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # สร้าง JWT token สำหรับรีเซ็ตรหัสผ่าน (หมดอายุใน 1 ชั่วโมง)
        reset_token = jwt.encode(
            {
                "user_id": getattr(user, "user_id", None) or getattr(user, "admin_id", None),
                "email": email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256"
        )

        # สร้างลิงก์สำหรับรีเซ็ตรหัสผ่าน
        frontend_url = current_app.config.get('FRONTEND_RETURN_URL', 'http://localhost:3000')
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

        # สร้างและส่งอีเมลล์รีเซ็ตรหัสผ่าน
        msg = Message(
            subject="Reset Your Password",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[email],
            body=f"Click the link below to reset your password:\n\n{reset_link}\n\nThis link will expire in 1 hour."
        )
        mail = current_app.extensions.get("mail")
        mail.send(msg)

        return jsonify({"message": "Password reset email sent successfully"}), 200

    except Exception as e:
        logger.error(f"❌ Forgot password failed: {e}", exc_info=True)
        return jsonify({"error": "Failed to process password reset request"}), 500



# ✅ Route: Health Check
@auth_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200
