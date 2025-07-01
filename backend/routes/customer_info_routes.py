# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/customer_info_routes.py
from flask import Blueprint, request, jsonify
from backend.services.customer_info_service import CustomerInfoService  # Absolute import
import logging

# Initialize the Blueprint
customer_info_bp = Blueprint("customer_info", __name__)
logging.basicConfig(level=logging.DEBUG)


@customer_info_bp.route("/customer-info", methods=["POST"], endpoint="customer_info_create")
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
        extracted_from = data.get("extracted_from", "manual")  # Default value: "manual"

        if not customer_id:
            logging.error("❌ Missing required field: customer_id")
            return jsonify({"error": "customer_id is required"}), 400

        # Call the service to create customer info
        info = CustomerInfoService.create_customer_info(
            customer_id=customer_id,
            id_card_number=data.get("id_card_number"),
            driver_license_number=data.get("driver_license_number"),
            vehicle_registration=data.get("vehicle_registration"),
            policy_number=data.get("policy_number"),
            extracted_from=extracted_from
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


@customer_info_bp.route("/customer-info/<int:customer_id>", methods=["GET"], endpoint="customer_info_get")
def get_customer_info(customer_id):
    """
    API to fetch customer information by customer_id.
    """
    try:
        logging.debug(f"🔍 Fetching customer info for customer_id={customer_id}")

        # Call the service to fetch customer info
        info = CustomerInfoService.get_customer_info(customer_id)
        if not info:
            logging.warning(f"⚠️ No customer info found for customer_id={customer_id}")
            return jsonify({"error": "Customer info not found"}), 404

        logging.info(f"✅ Customer info fetched successfully for customer_id={customer_id}")
        return jsonify({"info": info}), 200

    except Exception as e:
        logging.exception("❌ Error while fetching customer info")
        return jsonify({"error": "An unexpected error occurred"}), 500


@customer_info_bp.route("/customer-info/<int:customer_id>", methods=["PUT"], endpoint="customer_info_update")
def update_customer_info(customer_id):
    """
    API to update customer information by customer_id.
    """
    try:
        data = request.get_json()
        if not data:
            logging.error("❌ Request body is empty or invalid")
            return jsonify({"error": "Request body must be JSON"}), 400

        logging.debug(f"📥 Received data for updating customer info: {data}")

        # Call the service to update customer info
        updated_info = CustomerInfoService.update_customer_info(customer_id, **data)
        if not updated_info:
            logging.warning(f"⚠️ Customer info not found for customer_id={customer_id}")
            return jsonify({"error": "Customer info not found"}), 404

        logging.info(f"✅ Customer info updated successfully for customer_id={customer_id}")
        return jsonify({
            "message": "Customer info updated successfully",
            "info": updated_info
        }), 200

    except ValueError as ve:
        logging.warning(f"⚠️ Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("❌ Error while updating customer info")
        return jsonify({"error": "An unexpected error occurred"}), 500


@customer_info_bp.route("/customer-info/<int:customer_id>", methods=["DELETE"], endpoint="customer_info_delete")
def delete_customer_info(customer_id):
    """
    API to delete customer information by customer_id.
    """
    try:
        logging.debug(f"🗑️ Deleting customer info for customer_id={customer_id}")

        # Call the service to delete customer info
        deletion_result = CustomerInfoService.delete_customer_info(customer_id)
        if not deletion_result:
            logging.warning(f"⚠️ Customer info not found for customer_id={customer_id}")
            return jsonify({"error": "Customer info not found"}), 404

        logging.info(f"✅ Customer info deleted successfully for customer_id={customer_id}")
        return jsonify({"message": "Customer info deleted successfully"}), 200

    except Exception as e:
        logging.exception("❌ Error while deleting customer info")
        return jsonify({"error": "An unexpected error occurred"}), 500
