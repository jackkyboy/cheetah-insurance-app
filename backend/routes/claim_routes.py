# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/claim_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.claim_service import ClaimService
from backend.models.CustomerPolicies import CustomerPolicies
import logging

# Initialize Blueprint and Logger
claim_bp = Blueprint("claim", __name__, url_prefix="/api/claims")
logging.basicConfig(level=logging.DEBUG)


@claim_bp.route("/", methods=["POST"])
@jwt_required()
def report_claim():
    """
    API for reporting a claim issue
    """
    logging.info("📥 Received POST request for /api/claims")
    try:
        user_id = get_jwt_identity()
        logging.debug(f"🔑 JWT user_id: {user_id}")

        # Retrieve data from the request
        data = request.form
        policy_number = data.get("policy_number", None)
        policy_id = data.get("policy_id", None)
        description = data.get("description", "").strip()
        documents = request.files.getlist("documents")

        # Validate required fields
        if not description:
            logging.error("❌ Missing required field: description")
            return jsonify({"error": "Description is required"}), 400

        # Resolve policy_id using policy_number if provided
        if not policy_id and policy_number:
            policy = CustomerPolicies.query.filter_by(policy_number=policy_number, customer_id=user_id).first()
            if policy:
                policy_id = policy.policy_id
            else:
                logging.warning(f"⚠️ Policy number not found: {policy_number}")
                policy_id = None  # Proceed with a null policy_id for general claims

        # Process claim with ClaimService
        issue = ClaimService.report_claim_issue(
            user_id=user_id,
            policy_id=policy_id,
            description=description,
            documents=documents,
        )
        logging.info(f"✅ Claim issue reported successfully: issue_id={issue.issue_id}")

        return jsonify({"message": "Claim reported successfully", "issue_id": issue.issue_id}), 201

    except ValueError as ve:
        logging.warning(f"⚠️ Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("❌ Error while reporting claim")
        return jsonify({"error": "An unexpected error occurred"}), 500




@claim_bp.route("/<int:issue_id>", methods=["PUT"])
@jwt_required()
def update_claim(issue_id):
    """
    API for updating a claim issue
    """
    logging.info(f"📥 Received PUT request for /api/claims/{issue_id}")
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        status = data.get("status")
        response = data.get("response", None)

        if not status:
            logging.error("❌ Missing required field: status")
            return jsonify({"error": "status is required"}), 400

        # Update the claim
        issue = ClaimService.update_claim_status(issue_id, status, response, user_id)
        logging.info(f"✅ Claim issue updated successfully: issue_id={issue_id}, status={status}")

        return jsonify({"message": "Claim status updated successfully", "issue_id": issue.issue_id, "status": issue.status}), 200

    except ValueError as ve:
        logging.warning(f"⚠️ Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("❌ Error while updating claim")
        return jsonify({"error": "An unexpected error occurred"}), 500


@claim_bp.route("/policy/<int:policy_id>", methods=["GET"])
@jwt_required()
def get_claims_by_policy(policy_id):
    """
    API for fetching claims associated with a policy
    """
    logging.info(f"📥 Received GET request for /api/claims/policy/{policy_id}")
    try:
        user_id = get_jwt_identity()
        logging.debug(f"🔍 Fetching claims for policy_id={policy_id} by user_id={user_id}")

        issues = ClaimService.get_claim_issues_by_policy(policy_id, user_id)
        logging.info(f"✅ Fetched {len(issues)} issues for policy_id={policy_id}")

        return jsonify({"issues": issues}), 200

    except Exception as e:
        logging.exception("❌ Error while fetching claims by policy")
        return jsonify({"error": "An unexpected error occurred"}), 500


@claim_bp.route("/<int:issue_id>", methods=["GET"])
@jwt_required()
def get_claim_by_id(issue_id):
    """
    API for fetching claim details by issue ID
    """
    logging.info(f"📥 Received GET request for /api/claims/{issue_id}")
    try:
        user_id = get_jwt_identity()
        logging.debug(f"🔍 Fetching claim issue_id={issue_id} for user_id={user_id}")

        issue = ClaimService.get_claim_issue_by_id(issue_id, user_id)
        if not issue:
            logging.warning(f"⚠️ Claim issue not found: issue_id={issue_id}")
            return jsonify({"error": "Claim issue not found"}), 404

        logging.info(f"✅ Fetched claim issue successfully: issue_id={issue_id}")
        return jsonify(issue), 200

    except ValueError as ve:
        logging.warning(f"⚠️ Validation error: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logging.exception("❌ Error while fetching claim by ID")
        return jsonify({"error": "An unexpected error occurred"}), 500
