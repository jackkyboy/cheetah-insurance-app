# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/policy_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.policy_service import PolicyService  # Absolute import
import logging

# สร้าง Blueprint
policy_bp = Blueprint("policy", __name__)

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@policy_bp.route("/policies", methods=["POST"])
@jwt_required()
def create_policy():
    """
    API สำหรับสร้างกรมธรรม์ใหม่
    """
    try:
        data = request.json
        customer_id = data.get("customer_id")
        package_id = data.get("package_id")

        if not customer_id or not package_id:
            logger.warning("❌ customer_id or package_id is missing")
            return jsonify({"error": "customer_id and package_id are required"}), 400

        policy = PolicyService.create_policy(
            customer_id=customer_id,
            package_id=package_id,
            policy_number=data.get("policy_number"),
            insurance_response=data.get("insurance_response")
        )

        logger.info(f"✅ Policy created successfully: policy_id={policy.policy_id}")
        return jsonify({"message": "Policy created successfully", "policy_id": policy.policy_id}), 201
    except Exception as e:
        logger.exception("❌ Error creating policy")
        return jsonify({"error": "An error occurred while creating policy"}), 500


@policy_bp.route("/policies/<int:policy_id>", methods=["GET"])
@jwt_required()
def get_policy(policy_id):
    """
    API สำหรับดึงข้อมูลกรมธรรม์จาก policy_id
    """
    try:
        logger.debug(f"🔍 Fetching policy for policy_id={policy_id}")
        policy = PolicyService.get_policy_by_id(policy_id)
        if not policy:
            logger.warning(f"⚠️ Policy not found: policy_id={policy_id}")
            return jsonify({"error": "Policy not found"}), 404

        logger.info(f"✅ Policy fetched successfully: policy_id={policy.policy_id}")
        return jsonify({
            'policy_id': policy.policy_id,
            'customer_id': policy.customer_id,
            'package_id': policy.package_id,
            'status': policy.status,
            'policy_number': policy.policy_number,
            'insurance_company_response': policy.insurance_company_response,
            'request_date': policy.request_date
        }), 200
    except Exception as e:
        logger.exception(f"❌ Error fetching policy: policy_id={policy_id}")
        return jsonify({"error": "An error occurred while fetching policy"}), 500


@policy_bp.route("/policies/customer/<int:customer_id>", methods=["GET"])
@jwt_required()
def get_policies_by_customer(customer_id):
    """
    API สำหรับดึงข้อมูลกรมธรรม์ทั้งหมดของลูกค้า
    """
    try:
        logger.debug(f"🔍 Fetching policies for customer_id={customer_id}")
        policies = PolicyService.get_policies_by_customer(customer_id)

        logger.info(f"✅ Policies fetched successfully for customer_id={customer_id}")
        return jsonify({"policies": policies}), 200
    except Exception as e:
        logger.exception(f"❌ Error fetching policies for customer_id={customer_id}")
        return jsonify({"error": "An error occurred while fetching policies"}), 500


@policy_bp.route("/policies/<int:policy_id>", methods=["PUT"])
@jwt_required()
def update_policy_status(policy_id):
    """
    API สำหรับอัปเดตสถานะกรมธรรม์
    """
    try:
        data = request.json
        status = data.get("status")
        if not status:
            logger.warning("❌ Missing required field: status")
            return jsonify({"error": "status is required"}), 400

        logger.debug(f"🔄 Updating policy: policy_id={policy_id} with status={status}")
        policy = PolicyService.update_policy_status(
            policy_id=policy_id,
            status=status,
            policy_number=data.get("policy_number"),
            insurance_response=data.get("insurance_response")
        )

        logger.info(f"✅ Policy updated successfully: policy_id={policy.policy_id}, status={policy.status}")
        return jsonify({
            "message": "Policy updated successfully",
            "policy_id": policy.policy_id,
            "status": policy.status
        }), 200
    except Exception as e:
        logger.exception(f"❌ Error updating policy: policy_id={policy_id}")
        return jsonify({"error": "An error occurred while updating policy"}), 500


@policy_bp.route("/policies/<int:policy_id>", methods=["DELETE"])
@jwt_required()
def delete_policy(policy_id):
    """
    API สำหรับลบกรมธรรม์
    """
    try:
        logger.debug(f"🗑️ Deleting policy: policy_id={policy_id}")
        PolicyService.delete_policy(policy_id)
        logger.info(f"✅ Policy deleted successfully: policy_id={policy_id}")
        return jsonify({"message": "Policy deleted successfully"}), 200
    except ValueError as ve:
        logger.warning(f"⚠️ Policy not found: policy_id={policy_id}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.exception(f"❌ Error deleting policy: policy_id={policy_id}")
        return jsonify({"error": "An error occurred while deleting policy"}), 500
