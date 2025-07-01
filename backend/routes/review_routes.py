# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/review_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.review_service import ReviewService
import logging

# Initialize Blueprint
review_bp = Blueprint("review", __name__, url_prefix="/api/reviews")

# Logger setup
logger = logging.getLogger("review_routes")
logging.basicConfig(level=logging.DEBUG)

@review_bp.route("/", methods=["POST"])
@jwt_required()
def add_review():
    """
    API to add a new review.
    Requires JWT authentication.
    """
    try:
        customer_id = get_jwt_identity()
        logger.debug(f"Received add review request from customer_id: {customer_id}")

        data = request.get_json()
        if not data:
            logger.warning("No data received in request")
            return jsonify({"error": "Invalid request data"}), 400

        package_id = data.get("package_id")
        company_id = data.get("company_id")  # ✅ ต้องระบุเพิ่ม
        rating = data.get("rating")
        comment = data.get("comment")

        if not all([package_id, company_id, rating]):
            logger.warning("Missing required fields: package_id, company_id, or rating")
            return jsonify({"error": "package_id, company_id, and rating are required"}), 400

        if not (1 <= rating <= 5):
            logger.warning(f"Invalid rating value: {rating}")
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        # ✅ ส่งทั้ง 3 ไปยัง service
        review = ReviewService.add_review(customer_id, company_id, package_id, rating, comment)
        logger.info(f"Review successfully added by customer_id: {customer_id}")

        return jsonify({
            "message": "Review added successfully",
            "review": review
        }), 201

    except ValueError as ve:
        logger.warning(f"Validation error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.exception("Unexpected error occurred while adding review")
        return jsonify({"error": "An unexpected error occurred"}), 500


@review_bp.route("/package/<int:package_id>", methods=["GET"])
@jwt_required()
def get_reviews_for_package(package_id):
    try:
        logger.debug(f"Fetching reviews for package_id: {package_id}")
        reviews = ReviewService.get_reviews_for_package(package_id)
        logger.info(f"Retrieved {len(reviews)} reviews for package_id: {package_id}")
        return jsonify({"reviews": reviews}), 200
    except Exception as e:
        logger.exception(f"Error fetching reviews for package_id: {package_id}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@review_bp.route("/customer", methods=["GET"])
@jwt_required()
def get_reviews_by_customer():
    try:
        customer_id = get_jwt_identity()
        logger.debug(f"Fetching reviews for customer_id: {customer_id}")
        reviews = ReviewService.get_reviews_by_customer(customer_id)
        logger.info(f"Fetched {len(reviews)} reviews for customer_id: {customer_id}")
        return jsonify({"reviews": reviews}), 200
    except Exception as e:
        logger.exception(f"Error fetching reviews for customer_id: {customer_id}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@review_bp.route("/average-ratings", methods=["GET"])
def get_average_ratings():
    try:
        logger.debug("Fetching average ratings for insurance companies")
        ratings_summary = ReviewService.get_average_ratings()
        logger.info(f"Fetched average ratings for {len(ratings_summary)} companies")
        return jsonify({"ratings": ratings_summary}), 200
    except Exception as e:
        logger.exception("Error fetching average ratings")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@review_bp.route("/summary", methods=["GET"])
@jwt_required(optional=True)
def get_insurance_reviews_summary():
    try:
        logger.debug("Fetching insurance reviews summary")
        summary = ReviewService.get_reviews_summary()
        logger.info(f"Fetched review summary for {len(summary)} companies")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        logger.exception("Error fetching insurance reviews summary")
        return jsonify({"error": "An unexpected error occurred"}), 500
