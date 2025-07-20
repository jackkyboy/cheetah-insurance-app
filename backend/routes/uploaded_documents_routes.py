# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/uploaded_documents_routes.py
from flask import Blueprint, jsonify, request, Response, send_from_directory
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from backend.models.Documents import Documents
from backend.models.Customers import Customers
from backend.models import db
import logging
import os
import re
from backend.models.Users import Users
from backend.services.uploaded_documents_service import UploadedDocumentsService

uploaded_documents_bp = Blueprint("uploaded_documents", __name__, url_prefix="/api/documents")
logger = logging.getLogger(__name__)

UPLOAD_DIR = "/Users/apichet/Downloads/cheetah-insurance-app/backend/uploads/documents"

# -------------------- Helper Functions --------------------


def extract_token():
    """
    ✅ ตรวจสอบ JWT และดึง user_id จาก token
    """
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        user_id = claims.get("user_id")
        if not user_id:
            raise ValueError("Token is missing user_id")
        return user_id
    except Exception as e:
        raise ValueError("Invalid or missing token") from e


def sanitize_filename(filename):
    """Sanitize the filename while preserving Thai Unicode characters."""
    sanitized = re.sub(r'[^\w\-.\s\u0E00-\u0E7F]', '_', filename, flags=re.UNICODE)
    logger.debug(f"Sanitized filename: {sanitized}")
    return sanitized


def _handle_options_request():
    """Handles CORS preflight requests."""
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response, 200

def _verify_jwt_and_get_user():
    """Verify JWT and return the current user info."""
    try:
        verify_jwt_in_request()
        decoded_token = get_jwt()

        logger.debug(f"🔍 Decoded JWT: {decoded_token}")

        user_id = decoded_token.get("user_id")
        admin_id = decoded_token.get("admin_id")
        role = decoded_token.get("role")

        if not user_id and not admin_id:
            logger.error(f"❌ JWT Token missing both 'user_id' and 'admin_id': {decoded_token}")
            return None  # ปรับให้ส่งค่า None แทน jsonify() เพื่อให้สามารถ return HTTP 403 ได้

        if not role:
            logger.warning(f"⚠️ JWT Token missing 'role': {decoded_token}")
            role = "admin" if admin_id else "user"

        user_info = {"user_id": user_id, "admin_id": admin_id, "role": role}
        logger.debug(f"✅ Token Verified. user_info={user_info}")
        return user_info

    except Exception as e:
        logger.exception("❌ JWT verification failed")
        return None


def _validate_required_fields(fields):
    """Validate required fields in a request."""
    missing_fields = [field for field, value in fields.items() if not value]
    if missing_fields:
        logger.warning(f"❌ Missing fields: {', '.join(missing_fields)}")
        return False, {"error": f"Missing required fields: {', '.join(missing_fields)}"}
    return True, {}

def _check_user_access(user, customer_id):
    """Check if the user has access to the specified customer."""
    try:
        if user["role"] == "admin":
            logger.info(f"✅ Admin access granted: admin_id={user['admin_id']}")
            return True

        user_id = user["user_id"]
        user_obj = Users.query.filter_by(user_id=user_id).first()
        if not user_obj:
            logger.warning(f"❌ User not found: user_id={user_id}")
            return False

        # ✅ แก้ตรงนี้: ดึง Customers โดยใช้ user_id
        customer_obj = Customers.query.filter_by(user_id=user_id).first()
        if not customer_obj:
            logger.warning(f"❌ No customer record found for user_id={user_id}")
            return False

        if str(customer_obj.customer_id) != str(customer_id):
            logger.warning(f"❌ Unauthorized access: customer_id mismatch ({customer_obj.customer_id} != {customer_id})")
            return False

        return True
    except Exception as e:
        logger.exception("❌ Error checking user access")
        return False



# -------------------- Routes --------------------

def serialize_document(doc):
    """แปลงเอกสารให้สามารถ jsonify ได้"""
    if hasattr(doc, "to_dict"):
        return doc.to_dict()
    return {
        "error": "Non-serializable object detected",
        "type": str(type(doc))
    }

@uploaded_documents_bp.route("/customer/<int:customer_id>", methods=["GET", "OPTIONS"], strict_slashes=False)
def get_documents_by_customer(customer_id):
    """📂 Fetch uploaded documents by customer ID."""
    if request.method == "OPTIONS":
        return _handle_options_request()

    user = _verify_jwt_and_get_user()
    if not user:
        logger.error("❌ Unauthorized: Unable to verify JWT.")
        return jsonify({"error": "Unauthorized"}), 403

    logger.debug(f"🔍 Checking access for user={user} and customer_id={customer_id}")
    if not _check_user_access(user, customer_id):
        logger.warning(f"❌ Access denied: user={user}, customer_id={customer_id}")
        return jsonify({"error": "Unauthorized"}), 403

    try:
        documents = UploadedDocumentsService.fetch_documents_by_customer(customer_id)

        if not documents:
            logger.info(f"⚠️ No documents found for customer_id={customer_id}")
            return jsonify({"documents": []}), 200

        serialized = [serialize_document(doc) for doc in documents]

        logger.info(f"✅ {len(serialized)} document(s) fetched for customer_id={customer_id}")
        return jsonify({"documents": serialized}), 200

    except Exception as e:
        logger.exception(f"❌ Unexpected error while fetching documents for customer_id={customer_id}")
        return jsonify({"error": "An unexpected error occurred"}), 500





@uploaded_documents_bp.route("", methods=["POST", "OPTIONS"], strict_slashes=False)
def upload_document():
    """Upload a document."""
    if request.method == "OPTIONS":
        return _handle_options_request()

    try:
        user = _verify_jwt_and_get_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 403

        # ✅ ตรวจสอบค่า customer_id จาก token ถ้าไม่ได้ส่งมา
        customer_id = request.form.get("customer_id")
        if not customer_id:
            customer_id = user.get("user_id")

        fields = {
            "customer_id": customer_id,
            "document_type": request.form.get("document_type"),
            "file": request.files.get("file"),
        }

        logger.debug(f"📥 Received upload data: {fields}")

        is_valid, error_response = _validate_required_fields(fields)
        if not is_valid:
            return jsonify(error_response), 400

        if not _check_user_access(user, fields["customer_id"]):
            return jsonify({"error": "Unauthorized access"}), 403

        document = UploadedDocumentsService.upload_document(
            customer_id=fields["customer_id"],
            document_type=fields["document_type"],
            file=fields["file"]
        )

        logger.info(f"✅ Document uploaded successfully for customer_id={fields['customer_id']}")
        return jsonify({"message": "Document uploaded successfully.", "document": document}), 201

    except Exception as e:
        logger.exception("❌ Error uploading document.")
        return jsonify({"error": "Failed to upload document"}), 500



@uploaded_documents_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_uploaded_file(filename):
    """
    Serve uploaded files securely to the client.
    """
    try:
        logger.info(f"📂 Attempting to serve file: {filename}")

        sanitized_filename = sanitize_filename(filename)
        logger.debug(f"🔒 Sanitized filename: {sanitized_filename}")

        safe_path = os.path.normpath(os.path.join(UPLOAD_DIR, sanitized_filename))
        logger.debug(f"🔒 Resolved safe path: {safe_path}")

        if not os.path.abspath(safe_path).startswith(os.path.abspath(UPLOAD_DIR)):
            logger.error(f"❌ Unauthorized file access attempt: {filename}")
            return send_from_directory('static/uploads/profile_pictures', 'default-profile.png')

        if not os.path.isfile(safe_path):
            logger.warning(f"❌ File not found: {safe_path}")
            return send_from_directory('static/uploads/profile_pictures', 'default-profile.png')

        logger.info(f"✅ Successfully serving file: {safe_path}")
        return send_from_directory(UPLOAD_DIR, sanitized_filename, as_attachment=False)

    except Exception as e:
        logger.exception("❌ Unexpected error while serving file")
        return jsonify({"error": "An unexpected error occurred"}), 500




@uploaded_documents_bp.route("/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
    try:
        user_id = extract_token()
        if not user_id:
            logger.warning("❌ Missing or invalid JWT token.")
            return jsonify({"error": "Unauthorized"}), 401

        document = Documents.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404

        if str(document.customer_id) != str(user_id):
            return jsonify({"error": "You do not have permission to delete this document."}), 403

        # ✅ ให้ service handle ทั้ง file + DB deletion
        UploadedDocumentsService.delete_document(document_id)
        logger.info(f"✅ Document deleted via service: id={document_id}")
        return jsonify({"message": "Document deleted successfully"}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 401
    except Exception as e:
        logger.exception("❌ Unexpected error while deleting document")
        return jsonify({"error": "An unexpected error occurred"}), 500
