# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/insurance_preparation_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db
from backend.models.InsurancePreparation import InsurancePreparation
from backend.models.Users import Users
import logging

# Initialize Blueprint
insurance_preparation_bp = Blueprint("insurance_preparation_bp", __name__)
logging.basicConfig(level=logging.DEBUG)

# Utility Function for Validation
def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in the request data."""
    missing_fields = [field for field in required_fields if not data.get(field)]
    return missing_fields


@insurance_preparation_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_insurance_preparation(user_id):
    """
    Fetch a specific insurance preparation for the authenticated user.
    """
    try:
        logging.info(f"🔍 [GET] Fetching insurance preparation for user_id={user_id}")
        
        jwt_user_id = get_jwt_identity()
        logging.debug(f"🔑 User ID from JWT: {jwt_user_id} (Expected user_id={user_id})")

        # Validate user identity
        if int(jwt_user_id) != user_id:
            logging.error(f"❌ Unauthorized access attempt: JWT user_id={jwt_user_id}, requested user_id={user_id}")
            return jsonify({"error": "Unauthorized access"}), 403

        logging.debug(f"🔍 Querying InsurancePreparation for user_id={user_id}")
        preparation = InsurancePreparation.query.filter_by(user_id=user_id).first()

        if not preparation:
            logging.warning(f"❌ No insurance preparation found for user_id={user_id}")
            return jsonify({"error": "Insurance preparation not found"}), 404

        logging.info(f"✅ Insurance preparation found for user_id={user_id}")
        return jsonify({"data": preparation.to_dict()}), 200

    except Exception as e:
        logging.exception("❌ Error fetching insurance preparation")
        return jsonify({"error": "An unexpected error occurred"}), 500


@insurance_preparation_bp.route("/", methods=["POST"])
@jwt_required()
def create_insurance_preparation():
    """
    Create a new insurance preparation entry.
    """
    try:
        logging.info("🔍 [POST] Starting insurance preparation creation process...")
        
        user_id = get_jwt_identity()
        logging.debug(f"🔑 User ID from JWT: {user_id}")

        user = Users.query.get(user_id)
        if not user:
            logging.error(f"❌ User with user_id={user_id} not found in the database.")
            return jsonify({"error": "User not found"}), 404

        data = request.get_json()
        logging.debug(f"📥 Received data: {data}")

        required_fields = ["insured_info", "motor_info", "policy_info"]
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            logging.error(f"❌ Missing required fields: {missing_fields}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        insured_info = data.get("insured_info", {})
        insured_info["InsuredEmail"] = user.email
        data["insured_info"] = insured_info

        logging.debug(f"📦 Creating new InsurancePreparation entry for user_id={user_id}")
        new_entry = InsurancePreparation(
            user_id=user_id,
            insured_info=data.get("insured_info"),
            motor_info=data.get("motor_info"),
            policy_info=data.get("policy_info"),
            driver_info=data.get("driver_info"),
            beneficiary_info=data.get("beneficiary_info"),
            coverage_info=data.get("coverage_info"),
            consent_info=data.get("consent_info"),
        )
        db.session.add(new_entry)
        db.session.commit()

        logging.info(f"✅ Insurance preparation created successfully for user_id={user_id}")
        return jsonify({
            "message": "Insurance preparation created successfully",
            "data": new_entry.to_dict()
        }), 201

    except Exception as e:
        logging.exception("❌ Error creating insurance preparation")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@insurance_preparation_bp.route("/", methods=["GET"])
@jwt_required()
def get_insurance_preparations():
    """
    Fetch all insurance preparations for the authenticated user.
    """
    try:
        user_id = get_jwt_identity()
        logging.info(f"🔍 [GET] Fetching all insurance preparations for user_id={user_id}")

        entries = InsurancePreparation.query.filter_by(user_id=user_id).all()
        if not entries:
            logging.warning(f"❌ No insurance preparations found for user_id={user_id}")

        result = [entry.to_dict() for entry in entries]
        logging.info(f"✅ Retrieved {len(result)} insurance preparations for user_id={user_id}")
        return jsonify({"data": result}), 200

    except Exception as e:
        logging.exception("❌ Error fetching insurance preparations")
        return jsonify({"error": "An unexpected error occurred"}), 500


@insurance_preparation_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def update_insurance_preparation(id):
    """
    Update an existing insurance preparation.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        logging.info(f"🔍 [PUT] Updating insurance preparation id={id} for user_id={user_id}")
        logging.debug(f"📥 Data for update: {data}")

        entry = InsurancePreparation.query.filter_by(id=id, user_id=user_id).first()
        if not entry:
            logging.warning(f"❌ Insurance preparation not found for id={id} and user_id={user_id}")
            return jsonify({"error": "Insurance preparation not found"}), 404

        logging.debug(f"Before update: {entry.to_dict()}")

        fields_to_update = [
            "insured_info", "motor_info", "policy_info", "driver_info",
            "beneficiary_info", "coverage_info", "consent_info"
        ]
        for field in fields_to_update:
            if data.get(field):
                logging.debug(f"Updating field {field} with data: {data[field]}")
                setattr(entry, field, data[field])

        db.session.commit()
        logging.debug(f"After update: {entry.to_dict()}")
        logging.info(f"✅ Insurance preparation updated successfully for id={id}")
        return jsonify({
            "message": "Insurance preparation updated successfully",
            "data": entry.to_dict()
        }), 200

    except Exception as e:
        logging.exception("❌ Error updating insurance preparation")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500



@insurance_preparation_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_insurance_preparation(id):
    """
    Delete an insurance preparation entry.
    """
    try:
        user_id = get_jwt_identity()
        logging.info(f"🔍 [DELETE] Deleting insurance preparation id={id} for user_id={user_id}")

        entry = InsurancePreparation.query.filter_by(id=id, user_id=user_id).first()
        if not entry:
            logging.warning(f"❌ Insurance preparation not found for id={id}")
            return jsonify({"error": "Insurance preparation not found"}), 404

        db.session.delete(entry)
        db.session.commit()
        logging.info(f"✅ Insurance preparation deleted successfully for id={id}")
        return jsonify({"message": "Insurance preparation deleted successfully"}), 200

    except Exception as e:
        logging.exception("❌ Error deleting insurance preparation")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500
