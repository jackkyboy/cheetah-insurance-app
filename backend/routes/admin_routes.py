# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/admin_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from backend.services.admin_service import AdminService
from functools import wraps
import logging
from backend.config.config import Config
from backend.utils.jwt_utils import generate_jwt, generate_refresh_token

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# JWT Secret Key
JWT_SECRET_KEY = Config.JWT_SECRET_KEY

# Create Admin Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/api/admins")


# Middleware: Admin Role Validation
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()

            # ✅ ตรวจสอบว่า identity เป็น string และแปลงเป็น dict
            if isinstance(identity, str):
                logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
                identity = {"admin_id": identity, "role": "admin"}  

            if not isinstance(identity, dict) or identity.get("role") not in ["admin", "superadmin"]:
                logger.warning(f"❌ Unauthorized access attempt by: {identity}")
                return jsonify({"error": "Admins only!"}), 403

            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"❌ Authorization error: {e}")
            return jsonify({"error": "Unauthorized"}), 401

    return decorated_function




# ✅ Create a New Admin
@admin_bp.route("", methods=["POST"])
@jwt_required()
@admin_required
def create_admin():
    try:
        current_user = get_jwt_identity()
        data = request.json
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "admin")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        admin = AdminService.create_admin(email, password, role, created_by=current_user["admin_id"])
        return jsonify({"message": "Admin created successfully", "admin": admin}), 201
    except Exception as e:
        logger.error(f"❌ Error creating admin: {e}")
        return jsonify({"error": str(e)}), 500


# ✅ Admin Login# ✅ Admin Login
@admin_bp.route("/login", methods=["POST"])
def login_admin():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        tokens = AdminService.login_admin(email, password)

        if not tokens or "access_token" not in tokens:
            logger.error("❌ Login failed: No access token returned.")
            return jsonify({"error": "Login failed"}), 401

        logger.info(f"✅ Admin {email} logged in successfully")
        return jsonify({
            "message": "Login successful",
            "access_token": tokens["access_token"],
            "refresh_token": tokens.get("refresh_token")
        }), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return jsonify({"error": "Unexpected server error"}), 500



# ✅ Get All Admins
# ✅ Get All Admins
@admin_bp.route("/", methods=["GET"])
@jwt_required()
@admin_required
def get_all_admins():
    try:
        admins = AdminService.get_all_admins()
        return jsonify({"admins": admins}), 200
    except Exception as e:
        logger.error(f"❌ Error fetching admins: {e}")
        return jsonify({"error": "Server error"}), 500


# ✅ Get Current Admin Info
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/admin_routes.py

@admin_bp.route("/me", methods=["GET"])
@jwt_required()
def get_admin_info():
    """
    ดึงข้อมูลโปรไฟล์ของ Admin
    """
    try:
        identity = get_jwt_identity()

        # ✅ ตรวจสอบให้ identity เป็น dict เสมอ
        if isinstance(identity, str):
            logger.warning("⚠️ [ADMIN CHECK] Identity is string, converting to dict.")
            identity = {"admin_id": identity, "role": "admin"}

        logger.debug(f"🔍 Fetching admin info for: {identity}")

        admin_id = identity.get("admin_id")
        if not admin_id:
            logger.warning("⚠️ [ADMIN CHECK] admin_id missing in JWT identity.")
            return jsonify({"error": "Unauthorized"}), 401

        # ✅ ตรวจสอบว่ามี `get_admin_by_id()` จริง
        if not hasattr(AdminService, "get_admin_by_id"):
            logger.error("❌ [AdminService] Missing get_admin_by_id()")
            return jsonify({"error": "Server misconfiguration"}), 500

        # ✅ เรียกใช้งานฟังก์ชัน get_admin_by_id()
        admin = AdminService.get_admin_by_id(admin_id)

        if not admin:
            return jsonify({"error": "Admin not found"}), 404

        return jsonify({
            "admin_id": admin.admin_id,
            "name": admin.name if hasattr(admin, "name") else "N/A",
            "email": admin.email,
            "role": admin.role
        }), 200

    except Exception as e:
        logger.error(f"❌ Error retrieving admin info: {e}")
        return jsonify({"error": "Unexpected server error"}), 500

# ✅ Update Admin Details
@admin_bp.route("/<int:admin_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_admin(admin_id):
    try:
        data = request.json
        email = data.get("email")
        role = data.get("role")

        if not email and not role:
            return jsonify({"error": "At least one field (email or role) must be provided"}), 400

        updated_admin = AdminService.update_admin(admin_id, email=email, role=role)
        return jsonify({"message": "Admin updated successfully", "admin": updated_admin}), 200
    except Exception as e:
        logger.error(f"❌ Error updating admin: {e}")
        return jsonify({"error": "Unexpected server error"}), 500


# ✅ Delete Admin Account
@admin_bp.route("/<int:admin_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_admin(admin_id):
    try:
        result = AdminService.delete_admin(admin_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"❌ Error deleting admin: {e}")
        return jsonify({"error": "Unexpected server error"}), 500


# ✅ Get Pending Users (New API)
@admin_bp.route("/pending-users", methods=["GET"])
@jwt_required()
@admin_required
def get_pending_users():
    try:
        pending_users = AdminService.get_pending_users()
        return jsonify({"pending_users": pending_users}), 200
    except Exception as e:
        logger.error(f"❌ Error fetching pending users: {e}")
        return jsonify({"error": "Server error"}), 500


# ✅ Fetch Dashboard Stats (New API)
@admin_bp.route("/dashboard-stats", methods=["GET"])
@jwt_required()
@admin_required
def get_dashboard_stats():
    try:
        logger.info("📊 Fetching Dashboard Stats...")
        stats = AdminService.get_dashboard_stats()

        if "error" in stats:
            return jsonify({"error": stats["error"]}), 500

        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"❌ Error fetching dashboard stats: {e}")
        return jsonify({"error": "Server error"}), 500




# ✅ Approve User (New API)
@admin_bp.route("/approve-user", methods=["POST"])
@jwt_required()
@admin_required
def approve_user():
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        AdminService.approve_user(user_id, approved_by=get_jwt_identity()["admin_id"])
        return jsonify({"message": "User approved successfully"}), 200
    except Exception as e:
        logger.error(f"❌ Error approving user: {e}")
        return jsonify({"error": "Server error"}), 500


# ✅ Reject User (New API)
@admin_bp.route("/reject-user", methods=["POST"])
@jwt_required()
@admin_required
def reject_user():
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        AdminService.reject_user(user_id, rejected_by=get_jwt_identity()["admin_id"])
        return jsonify({"message": "User rejected successfully"}), 200
    except Exception as e:
        logger.error(f"❌ Error rejecting user: {e}")
        return jsonify({"error": "Server error"}), 500
