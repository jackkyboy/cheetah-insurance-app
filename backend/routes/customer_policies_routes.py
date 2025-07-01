# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/customer_policies_routes.py
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.CustomerPolicies import CustomerPolicies  # Import the model for CustomerPolicies
import logging

# Initialize Blueprint
customer_policies_bp = Blueprint("customer_policies", __name__)
logging.basicConfig(level=logging.DEBUG)

# Utility Function for Validation
def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in the request data."""
    missing_fields = [field for field in required_fields if not data.get(field)]
    return missing_fields

# Example route (optional, can be removed)
@customer_policies_bp.route("/example", methods=["GET"])
def example():
    return "Customer Policies Route Example"

# Get all policies for a specific customer
@customer_policies_bp.route("/customer/<int:customer_id>", methods=["GET"])
def get_policies_by_customer(customer_id):
    """
    Fetch all policies for a specific customer.
    """
    try:
        logging.info(f"🔍 Fetching policies for customer_id={customer_id}")
        policies = CustomerPolicies.query.filter_by(customer_id=customer_id).all()
        if not policies:
            logging.warning(f"❌ No policies found for customer_id={customer_id}")
            return jsonify({"message": "No policies found", "data": []}), 404

        logging.info(f"✅ Retrieved {len(policies)} policies for customer_id={customer_id}")
        return jsonify({"data": [policy.to_dict() for policy in policies]}), 200
    except Exception as e:
        logging.exception("❌ Error fetching policies")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Create a new policy for a customer
@customer_policies_bp.route("/create", methods=["POST"])
def create_policy():
    """
    Create a new policy for a customer.
    """
    try:
        data = request.get_json()
        logging.info("🔍 Creating a new policy")
        logging.debug(f"📥 Received data: {data}")

        # Validate required fields
        required_fields = ["customer_id", "policy_details"]
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            logging.error(f"❌ Missing required fields: {missing_fields}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Create new policy
        new_policy = CustomerPolicies(
            customer_id=data["customer_id"],
            policy_details=data["policy_details"],
            premium=data.get("premium"),
            coverage=data.get("coverage"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            policy_number=data.get("policy_number"),
        )
        db.session.add(new_policy)
        db.session.commit()

        logging.info(f"✅ Policy created successfully for customer_id={data['customer_id']}")
        return jsonify({"message": "Policy created successfully", "data": new_policy.to_dict()}), 201
    except Exception as e:
        logging.exception("❌ Error creating policy")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500

# Update an existing policy
@customer_policies_bp.route("/<int:policy_id>", methods=["PUT"])
def update_policy(policy_id):
    """
    Update an existing policy by policy_id.
    """
    try:
        data = request.get_json()
        logging.info(f"🔍 Updating policy_id={policy_id}")
        logging.debug(f"📥 Data for update: {data}")

        policy = CustomerPolicies.query.get(policy_id)
        if not policy:
            logging.warning(f"❌ Policy not found for policy_id={policy_id}")
            return jsonify({"error": "Policy not found"}), 404

        # Update fields dynamically
        updatable_fields = ["policy_details", "premium", "coverage", "start_date", "end_date", "policy_number"]
        for field in updatable_fields:
            if field in data:
                setattr(policy, field, data[field])

        db.session.commit()
        logging.info(f"✅ Policy updated successfully for policy_id={policy_id}")
        return jsonify({"message": "Policy updated successfully", "data": policy.to_dict()}), 200
    except Exception as e:
        logging.exception("❌ Error updating policy")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500

# Delete a policy by policy_id
@customer_policies_bp.route("/<int:policy_id>", methods=["DELETE"])
def delete_policy(policy_id):
    """
    Delete a policy by policy_id.
    """
    try:
        logging.info(f"🔍 Deleting policy_id={policy_id}")
        policy = CustomerPolicies.query.get(policy_id)
        if not policy:
            logging.warning(f"❌ Policy not found for policy_id={policy_id}")
            return jsonify({"error": "Policy not found"}), 404

        db.session.delete(policy)
        db.session.commit()
        logging.info(f"✅ Policy deleted successfully for policy_id={policy_id}")
        return jsonify({"message": "Policy deleted successfully"}), 200
    except Exception as e:
        logging.exception("❌ Error deleting policy")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500
