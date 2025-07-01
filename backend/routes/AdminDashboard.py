# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/AdminDashboard.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request, get_jwt_identity
from flask_cors import cross_origin
from functools import wraps
import logging
from backend.config.config import Config
from backend.services.admin_service import AdminService

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# JWT Secret Key
JWT_SECRET_KEY = Config.JWT_SECRET_KEY

# Create Admin Blueprint
admin_bp = Blueprint("admin", __name__)

# ✅ Middleware: Admin Role Validation
def authorize_admin_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            jwt_payload = get_jwt_identity()

            # ✅ แปลง identity เป็น dictionary เสมอ
            if isinstance(jwt_payload, str):
                logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
                jwt_payload = {"admin_id": jwt_payload, "role": "admin"}

            logger.debug(f"✅ [Admin Access] Token Verified: {jwt_payload}")

            # ✅ ใช้ role จาก jwt_payload
            role = jwt_payload.get("role")
            if role not in ["admin", "superadmin"]:
                logger.warning(f"❌ [Admin Access] Unauthorized. Role: {role}")
                return jsonify({"error": "Unauthorized. Admin role required."}), 403
        except Exception as e:
            logger.warning(f"❌ [Admin Access] Invalid JWT Token: {e}")
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated_function


# ✅ Standard Response Helper
def make_response(success, data=None, error=None, status=200):
    return jsonify({"success": success, "data": data, "error": error}), status

# ✅ Admin Login
@admin_bp.route("/login", methods=["POST"])
@cross_origin()
def login_admin():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return make_response(False, error="Email and password are required", status=400)

        tokens = AdminService.login_admin(email, password)
        if not tokens:
            logger.error(f"❌ Login failed for {email}")
            return make_response(False, error="Invalid credentials", status=401)

        logger.info(f"✅ Login successful for {email}")
        return make_response(True, data={"access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]})
    except ValueError as ve:
        return make_response(False, error=str(ve), status=401)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return make_response(False, error="Unexpected server error", status=500)

# 📊 GET: Fetch Dashboard Stats
@admin_bp.route("/dashboard-stats", methods=["GET"])
@authorize_admin_access
def get_dashboard_stats():
    try:
        jwt_payload = get_jwt_identity()

        # ✅ ตรวจสอบและแปลง identity ให้เป็น dictionary
        if isinstance(jwt_payload, str):
            logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
            jwt_payload = {"admin_id": jwt_payload, "role": "admin"}

        role = jwt_payload.get("role")
        logger.debug(f"🔍 [get_dashboard_stats] User Role: {role}")

        if not role:
            logger.warning("❌ Invalid token payload: Missing role")
            return make_response(False, error="Unauthorized", status=401)

        stats = AdminService.get_dashboard_stats()
        return make_response(True, data=stats)
    except Exception as e:
        logger.error(f"❌ Error fetching dashboard stats: {str(e)}")
        return make_response(False, error="Server error", status=500)


# ✅ Approve User
@admin_bp.route("/approve-user", methods=["POST"])
@cross_origin()
@authorize_admin_access
def approve_user():
    try:
        jwt_payload = get_jwt_identity()

        # ✅ ตรวจสอบและแปลง identity ให้เป็น dictionary
        if isinstance(jwt_payload, str):
            logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
            jwt_payload = {"admin_id": jwt_payload, "role": "admin"}

        admin_id = jwt_payload.get("admin_id")

        data = request.json
        user_id = data.get("user_id")

        if not user_id:
            return make_response(False, error="User ID is required", status=400)

        logger.debug(f"✅ [approve_user] Admin {admin_id} approving User {user_id}")

        AdminService.approve_user(user_id, approved_by=admin_id)
        return make_response(True, data={"message": "User approved successfully"})
    except Exception as e:
        logger.error(f"❌ Error approving user: {e}")
        return make_response(False, error="Server error", status=500)

# ✅ Reject User
@admin_bp.route("/reject-user", methods=["POST"])
@cross_origin()
@authorize_admin_access
def reject_user():
    try:
        jwt_payload = get_jwt_identity()

        # ✅ ตรวจสอบและแปลง identity ให้เป็น dictionary
        if isinstance(jwt_payload, str):
            logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
            jwt_payload = {"admin_id": jwt_payload, "role": "admin"}

        admin_id = jwt_payload.get("admin_id")

        data = request.json
        user_id = data.get("user_id")

        if not user_id:
            return make_response(False, error="User ID is required", status=400)

        logger.debug(f"✅ [reject_user] Admin {admin_id} rejecting User {user_id}")

        AdminService.reject_user(user_id, rejected_by=admin_id)
        return make_response(True, data={"message": "User rejected successfully"})
    except Exception as e:
        logger.error(f"❌ Error rejecting user: {e}")
        return make_response(False, error="Server error", status=500)
