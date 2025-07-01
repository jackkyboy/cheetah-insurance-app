# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/user_routes.py
from flask import Blueprint, request, jsonify
from flask import send_from_directory
from backend.services.user_service import UserService
from backend.models import db
from backend.models.Users import Users
from backend.models.Customers import Customers  # Import Customers
from backend.config.config import Config
from backend.models.CarInfo import CarInfo
from backend.utils.jwt_utils import decode_jwt 
from backend.models.Documents import Documents  
from sqlalchemy.orm import joinedload
from backend.routes.customer_info_routes import customer_info_bp
from werkzeug.utils import secure_filename
import os
import logging
import re
import jwt
from urllib.parse import unquote
from flask import send_file
from backend.services.customer_info_service import CustomerInfoService
import uuid
import datetime
from werkzeug.utils import safe_join

UPLOAD_DIR = "/Users/apichet/Downloads/cheetah-insurance-app/backend/uploads/profile_pictures"


# Initialize Blueprint
user_bp = Blueprint("user", __name__)
logging.basicConfig(level=logging.DEBUG)

# Load JWT Secret Key from Configปๆดก
JWT_SECRET_KEY = Config.JWT_SECRET_KEY

# Email regex pattern for validation
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Allowed file extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "doc", "docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Helper Functions
def validate_email(email):
    if not re.match(EMAIL_REGEX, email):
        raise ValueError("Invalid email format")

def validate_password(password):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters")

# Register User
@user_bp.route("/customer-info", methods=["POST"])
def create_customer_info():
    """
    API to create customer information.
    """
    try:
        data = request.get_json()
        if not data:
            logging.error("❌ Request body is empty or invalid")
            return jsonify({"error": "Request body must be JSON"}), 400

        logging.debug(f"📥 Received data for creating customer info: {data}")

        # Validate required fields
        customer_id = data.get("customer_id")
        id_card_number = data.get("id_card_number")
        if not customer_id:
            logging.error("❌ Missing required field: customer_id")
            return jsonify({"error": "customer_id is required"}), 400

        if id_card_number and len(id_card_number) != 13:
            logging.error("❌ Invalid ID card number format")
            return jsonify({"error": "Invalid ID card number format"}), 400

        # Call the service to create customer info
        info = CustomerInfoService.create_customer_info(
            customer_id=customer_id,
            id_card_number=id_card_number,
            driver_license_number=data.get("driver_license_number"),
            vehicle_registration=data.get("vehicle_registration"),
            policy_number=data.get("policy_number"),
            extracted_from=data.get("extracted_from", "manual")  # Default to "manual"
        )

        logging.info(f"✅ Customer info created successfully for customer_id={customer_id}")
        return jsonify({
            "message": "Customer info created successfully",
            "info": info
        }), 201

    except ValueError as ve:
        logging.warning(f"⚠️ Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("❌ Error while creating customer info")
        return jsonify({"error": "An unexpected error occurred"}), 500



# Get User Profile
@user_bp.route("/profile", methods=["GET"])
def get_profile():
    try:
        logging.debug("🔍 Profile endpoint accessed")
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logging.error("❌ Missing Authorization Header")
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = decode_jwt(token)
        logging.debug(f"✅ Decoded Token: {decoded_token}")

        user_id = decoded_token.get("user_id")
        if not user_id:
            logging.error("❌ Invalid token payload")
            return jsonify({"error": "Invalid token payload"}), 401

        profile = UserService.get_profile_with_documents(user_id)
        profile["user"]["profile_picture"] = profile["user"].get("profile_picture") or "/static/images/default-profile.png"

        logging.info(f"✅ Profile fetched successfully for user_id={user_id}")
        return jsonify(profile), 200
    except jwt.ExpiredSignatureError:
        logging.error("❌ Token has expired")
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logging.error("❌ Invalid token")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logging.exception("❌ Profile fetch error")
        return jsonify({"error": "An unexpected error occurred"}), 500


# Update User Profile
@user_bp.route("/profile", methods=["PUT"])
def update_profile():
    try:
        logging.debug("🔍 Profile update endpoint accessed")
        if not request.is_json:
            logging.error("❌ Invalid request payload: Expected JSON")
            return jsonify({"error": "Invalid request payload: Expected JSON"}), 400

        data = request.get_json()
        logging.debug(f"📥 Received payload: {data}")

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logging.error("❌ Missing Authorization Header")
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")
        logging.debug(f"✅ Decoded user_id: {user_id}")

        user = Users.query.options(
            joinedload(Users.customer).joinedload(Customers.car_info),
            joinedload(Users.customer).joinedload(Customers.documents)
        ).filter_by(user_id=user_id).first()

        if not user:
            logging.error(f"❌ User not found for user_id={user_id}")
            return jsonify({"error": "User not found"}), 404

        customer = user.customer
        fields_updated = False

        if "first_name" in data:
            customer.first_name = data["first_name"]
            fields_updated = True

        if "last_name" in data:
            customer.last_name = data["last_name"]
            fields_updated = True

        if "phone_number" in data:
            customer.phone_number = data["phone_number"]
            fields_updated = True

        if "profile_picture" in data:
            # ✅ ensure correct path format: always start with /uploads/
            picture = data["profile_picture"]
            if picture and not picture.startswith("/uploads/"):
                picture = f"/uploads/profile_pictures/{picture}"
            user.profile_picture = picture
            fields_updated = True

        if "car_info" in data:
            car_info_data = data["car_info"]
            logging.debug(f"🔧 Updating car_info: {car_info_data}")
            car_info = CarInfo.query.filter_by(customer_id=customer.customer_id).first()
            if car_info:
                car_info.car_brand = car_info_data.get("car_brand", car_info.car_brand)
                car_info.car_model = car_info_data.get("car_model", car_info.car_model)
                car_info.car_year = car_info_data.get("car_year", car_info.car_year)
                car_info.car_submodel = car_info_data.get("car_submodel", car_info.car_submodel)
                logging.info(f"🔄 Updated existing car_info for customer_id={customer.customer_id}")
            else:
                new_car_info = CarInfo(
                    customer_id=customer.customer_id,
                    car_brand=car_info_data.get("car_brand"),
                    car_model=car_info_data.get("car_model"),
                    car_year=car_info_data.get("car_year"),
                    car_submodel=car_info_data.get("car_submodel"),
                )
                db.session.add(new_car_info)
                logging.info(f"✨ Created new car_info for customer_id={customer.customer_id}")
            fields_updated = True

        if fields_updated:
            db.session.commit()
            logging.info(f"✅ Profile updated successfully for user_id={user_id}")

        updated_profile = UserService.get_profile_with_documents(user_id)

        # ✅ Ensure default picture format always begins with /uploads/
        updated_profile["user"]["profile_picture"] = (
            updated_profile["user"].get("profile_picture") or "/uploads/profile_pictures/default-profile.png"
        )

        return jsonify({
            "message": "Profile updated successfully",
            "user": updated_profile["user"],
            "customer": updated_profile["customer"],
            "car_info": updated_profile["car_info"],
        }), 200

    except jwt.ExpiredSignatureError:
        logging.error("❌ Token has expired")
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logging.error("❌ Invalid token")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logging.exception("❌ Profile update error")
        return jsonify({"error": "Unable to update profile"}), 500



def allowed_file(filename):
    """
    Validate if the file has an allowed extension.
    """
    if not filename or '.' not in filename:
        logging.warning(f"⚠️ Invalid filename or no extension provided: {filename}")
        return False

    extension = filename.rsplit('.', 1)[1].lower()
    if extension in ALLOWED_EXTENSIONS:
        logging.debug(f"✅ File is allowed with extension: {extension}")
        return True
    else:
        logging.warning(f"⚠️ Disallowed file extension: {extension}")
        return False



@user_bp.route("/customers/me", methods=["GET"])
def get_current_customer():
    """
    Fetch the current customer's information based on the JWT token.
    """
    try:
        # Decode JWT Token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            logging.error("❌ Missing Authorization header.")
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = decode_jwt(token)
        logging.debug(f"✅ Token decoded successfully: {decoded_token}")

        user_id = decoded_token.get("user_id")
        if not user_id:
            logging.error("❌ Token payload missing 'user_id'.")
            return jsonify({"error": "Invalid token payload"}), 401

        # Query Users and fetch related Customer
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            logging.warning(f"⚠️ User not found for user_id={user_id}")
            return jsonify({"error": "User not found"}), 404

        customer = user.customer
        if not customer:
            logging.warning(f"⚠️ Customer not found for user_id={user_id}")
            return jsonify({"error": "Customer not found"}), 404

        # Return customer information as JSON
        customer_data = customer.to_dict()
        logging.info(f"✅ Customer data fetched successfully for user_id={user_id}: {customer_data}")
        return jsonify(customer_data), 200

    except jwt.ExpiredSignatureError:
        logging.error("❌ Token has expired.")
        return jsonify({"error": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        logging.error("❌ Invalid token.")
        return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        logging.exception("❌ Error fetching current customer info.")
        return jsonify({"error": "An unexpected error occurred"}), 500
    
@user_bp.route("/documents", methods=["POST"])
def upload_document():
    try:
        logging.debug("📥 Uploading a document")

        # ตรวจสอบข้อมูลที่ได้รับ
        customer_id = request.form.get("customer_id")
        document_type = request.form.get("document_type")
        file = request.files.get("file")

        if not customer_id or not document_type or not file:
            logging.error("❌ Missing required fields")
            return jsonify({"error": "Missing required fields: customer_id, document_type, file"}), 400

        # ✅ ตรวจสอบและสร้างโฟลเดอร์อย่างปลอดภัย
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_DIR, filename)
        file.save(upload_path)

        # ✅ บันทึกข้อมูลเอกสารในฐานข้อมูล
        new_document = Documents(
            customer_id=customer_id,
            document_type=document_type,
            file_path=filename
        )
        db.session.add(new_document)
        db.session.commit()

        return jsonify({
            "message": "Document uploaded successfully",
            "document_id": new_document.document_id
        }), 201

    except Exception as e:
        logging.exception("❌ Error uploading document")
        return jsonify({"error": "An unexpected error occurred while uploading the document"}), 500





@user_bp.route("/profile-picture", methods=["POST"])
def upload_profile_picture():
    """
    Upload profile picture for authenticated user.
    """
    try:
        user_id = extract_token()
        file = request.files.get("file")

        if not file or not allowed_file(file.filename):
            return jsonify({"error": "Invalid or missing file"}), 400

        # สร้างโฟลเดอร์ถ้ายังไม่มี
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        # ตั้งชื่อไฟล์ให้ไม่ซ้ำ (uuid + timestamp)
        original_filename = secure_filename(file.filename)
        ext = os.path.splitext(original_filename)[1]
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{uuid.uuid4().hex}{ext}"
        upload_path = os.path.join(UPLOAD_DIR, unique_filename)
        file.save(upload_path)

        # อัปเดต path ลงในฐานข้อมูล
        user = Users.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # ✅ เปลี่ยน path ให้ชี้ผ่าน /api/
        relative_path = f"/uploads/profile_pictures/{unique_filename}"
        user.profile_picture = relative_path

        db.session.commit()

        return jsonify({
            "message": "Profile picture uploaded successfully",
            "profile_picture": relative_path   # ✅ เปลี่ยนตรงนี้
        }), 200


    except Exception as e:
        logging.exception("❌ Error uploading profile picture")
        return jsonify({"error": "An unexpected error occurred"}), 500



@user_bp.route("/documents/customer/<int:customer_id>", methods=["GET"])
def get_documents_by_customer(customer_id):
    """
    ดึงเอกสารทั้งหมดของลูกค้า
    """
    try:
        documents = Documents.query.filter_by(customer_id=customer_id).all()
        if not documents:
            return jsonify({"message": "No documents found"}), 404

        return jsonify({
            "documents": [doc.to_dict() for doc in documents]
        }), 200
    except Exception as e:
        logging.exception("❌ Error fetching documents")
        return jsonify({"error": "An unexpected error occurred"}), 500

# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/user_routes.py


def extract_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Authorization header is missing or invalid")
    
    token = auth_header.split(" ")[1]
    decoded_token = decode_jwt(token)
    user_id = decoded_token.get("user_id")
    if not user_id:
        raise ValueError("Invalid token payload")
    
    return user_id
