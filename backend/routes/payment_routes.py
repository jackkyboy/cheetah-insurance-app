# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/payment_routes.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/payment_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.payment_service import PaymentService
from backend.config.config import Config
from backend.services.gateway_2c2p import Gateway2C2P
import logging
import jwt
from datetime import datetime
from backend.models import db
from backend.models.Payments import Payments
from backend.models.Customers import Customers





# Initialize Blueprint for payment routes
payment_bp = Blueprint("payment_routes", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_payment_input(data, required_fields):
    """
    Validate the input data contains either a package_id or sufficient custom details.
    """
    missing_fields = []
    invalid_fields = []

    # Validate `amount`
    if "amount" not in data or not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
        invalid_fields.append("amount must be a positive number")

    # Validate `package_id`
    package_id = data.get("package_id")
    if package_id and not isinstance(package_id, int):
        invalid_fields.append("package_id must be an integer")

    # Check for additional required fields when `package_id` is missing
    if not package_id:
        additional_fields = ["insurance_type", "car_brand", "car_model"]
        missing_fields += [field for field in additional_fields if not data.get(field)]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    if invalid_fields:
        return False, f"Invalid fields: {', '.join(invalid_fields)}"

    return True, None




@payment_bp.route("/create", methods=["POST"])
@jwt_required()
def create_payment():
    """
    Create a new payment order.
    """
    try:
        logger.info("🔍 Received request to create payment.")

        # 🔐 Extract user identity
        user_id = get_jwt_identity()
        if not user_id:
            logger.warning("❌ Unauthorized access: Missing user ID.")
            return jsonify({"error": "Unauthorized"}), 401

        # 📥 Parse request payload
        data = request.json or {}
        logger.debug(f"📥 Request payload: {data}")

        # 🧼 Sanitize `package_id`
        try:
            package_id = int(data.get("package_id"))
        except (ValueError, TypeError):
            package_id = None
        data["package_id"] = package_id

        # 🔍 Validate customer ID
        customer_id = data.get("customer_id")
        if not customer_id:
            return jsonify({"error": "Customer ID is required"}), 400

        # ✅ Validate required fields
        required_fields = ["amount"] + ([] if package_id else ["insurance_type", "car_brand", "car_model"])
        is_valid, error_msg = validate_payment_input(data, required_fields)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # 🧾 Prepare payment metadata
        package_data = {
            "amount": data["amount"],
            "currency": data.get("currency", "THB"),
            "add_ons": data.get("add_ons", []),
            "coupon_code": data.get("coupon_code"),
            "insurance_type": data.get("insurance_type"),
            "car_brand": data.get("car_brand"),
            "car_model": data.get("car_model"),
            "car_submodel": data.get("car_submodel"),
            "car_year": data.get("car_year"),
            "description": data.get("description", "Custom Payment"),
            "package_id": package_id,
        }

        logger.info(f"💡 Payment details: {package_data}")

        # 🏗️ Create payment order
        payment_order = PaymentService.create_payment_order(customer_id, package_data)
        if not payment_order:
            return jsonify({"error": "Failed to create payment order"}), 500

        logger.info(f"✅ Payment order created: {payment_order}")

        # 🔐 Generate payment token
        payment_token = PaymentService.create_payment_token(
            invoice_no=payment_order["order_id"],
            amount=package_data["amount"],
            description=package_data["description"],
            country_code=data.get("country_code", "TH"),
            user_id=user_id,
        )
        if not payment_token:
            return jsonify({"error": "Failed to generate payment token"}), 500

        logger.info(f"✅ Payment token generated")

        # 🧾 Return final response
        return jsonify({
            "message": "Payment order created successfully",
            "payment_order": payment_order,
            "payload": payment_token,  # ✅ Fix key: payload
        }), 201

    except Exception as e:
        logger.exception("❌ Unexpected error occurred during payment creation")
        return jsonify({"error": "An error occurred while creating payment"}), 500



    

@payment_bp.route("/payments/status/<string:order_id>", methods=["GET"])
@jwt_required()
def get_payment_status(order_id):
    """
    Fetch the payment status from the database.
    """
    try:
        if not order_id:
            logger.warning("❌ Order ID is missing.")
            return jsonify({"error": "Order ID is required"}), 400

        payment_order = PaymentService.get_payment_order(order_id)
        if not payment_order:
            logger.warning(f"❌ Order not found for ID: {order_id}")
            return jsonify({"error": "Order not found"}), 404

        logger.info(f"✅ Payment status fetched successfully for order_id {order_id}: {payment_order}")
        return jsonify({
            "message": "Payment status fetched successfully",
            "payment_order": payment_order
        }), 200
    except Exception as e:
        logger.error(f"❌ Error fetching payment status: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching payment status"}), 500



@payment_bp.route("/do_payment", methods=["POST"])
def do_payment():
    """
    Endpoint to handle the payment process.
    """
    try:
        logger.info("🔧 Received request to process payment")

        # Log the raw request data for debugging
        logger.debug(f"🔍 Raw Request Data: {request.data}")
        
        # Parse JSON data
        data = request.get_json()
        logger.debug(f"✅ Parsed JSON Data: {data}")

        # Extract necessary fields
        payment_token = data.get("paymentToken")
        client_ip = data.get("clientIP")
        payment_details = data.get("payment")

        # Validate required fields
        if not payment_token or not client_ip or not payment_details:
            logger.error("❌ Missing required fields in the request")
            return jsonify({"error": "Missing required fields"}), 400

        logger.debug(f"🔍 Payment Token: {payment_token}")
        logger.debug(f"🔍 Client IP: {client_ip}")
        logger.debug(f"🔍 Payment Details: {payment_details}")

        # Process payment using Gateway2C2P
        response = Gateway2C2P.do_payment(payment_token, client_ip, payment_details)
        logger.info(f"✅ Payment response: {response}")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"❌ Error in do_payment: {e}", exc_info=True)
        return jsonify({"error": "Failed to process payment"}), 500


@payment_bp.route("/webhook", methods=["POST"])
def handle_payment_webhook():
    try:
        logger.info("🔧 Received webhook notification for payment.")
        data = request.get_json()
        logger.debug(f"✅ Webhook Payload: {data}")

        invoice_no = data.get("invoiceNo")
        status = data.get("status")

        if not invoice_no or not status:
            logger.error(f"❌ Missing invoiceNo or status: {data}")
            return jsonify({"error": "Missing invoiceNo or status"}), 400

        # Update the payment status
        updated = PaymentService.update_payment_status(invoice_no, status)
        if not updated:
            logger.error(f"❌ Payment order not found for invoiceNo: {invoice_no}")
            return jsonify({"error": "Payment order not found"}), 404

        logger.info(f"✅ Payment status updated successfully for invoiceNo: {invoice_no}")
        return jsonify({"message": "Payment status updated successfully"}), 200

    except Exception as e:
        logger.error(f"❌ Error processing webhook: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing webhook"}), 500


# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/payment_routes.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/payment_routes.py
# /backend/routes/payment_routes.py
@payment_bp.route("/status/<string:invoice_no>", methods=["GET"])
def get_payment_status_by_invoice(invoice_no):
    """
    Check payment status by invoice number.
    """
    try:
        logger.info(f"🔍 Checking payment status for invoice: {invoice_no}")
        
        payment_order = PaymentService.get_payment_order_status(invoice_no)
        if not payment_order:
            logger.warning(f"❌ Payment order not found for invoice: {invoice_no}")
            return jsonify({"error": "Payment order not found"}), 404
        
        logger.info(f"✅ Payment status found: {payment_order}")
        return jsonify({"message": "Payment status fetched successfully", "payment_order": payment_order}), 200
    except Exception as e:
        logger.error(f"❌ Error fetching payment status: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching payment status"}), 500
    



@payment_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_customer_orders():
    logger.debug(f"Incoming request for /orders")
    try:
        user_id = get_jwt_identity()
        logger.debug(f"Decoded user_id: {user_id}")
        customer = Customers.query.filter_by(user_id=user_id).first()
        logger.debug(f"Customer fetched: {customer}")

        if not customer:
            logger.warning(f"No customer found for user_id={user_id}")
            return jsonify({"error": "Customer not found"}), 404

        orders = Payments.query.filter_by(customer_id=customer.customer_id).all()
        logger.debug(f"Orders fetched: {orders}")

        if not orders:
            logger.info(f"No orders found for customer_id={customer.customer_id}")
            return jsonify({"orders": [], "message": "ยังไม่มีคำสั่งซื้อ"}), 200

        order_list = [order.to_dict() for order in orders]
        return jsonify({"orders": order_list}), 200
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching orders"}), 500




@payment_bp.route("/orders/customer/<int:customer_id>", methods=["GET"])
@jwt_required()
def get_orders_by_customer(customer_id):
    """
    Return all payment orders for a specific customer_id,
    but only if the authenticated user owns that customer.
    """
    try:
        user_id = get_jwt_identity()
        logger.debug(f"🔒 Verifying ownership: user_id={user_id} vs customer_id={customer_id}")

        customer = Customers.query.filter_by(customer_id=customer_id).first()

        if not customer:
            logger.warning(f"❌ Customer ID {customer_id} not found in DB.")
            return jsonify({"error": "Customer not found"}), 404

        # ✅ Fix: Compare user_id with casting to same type
        if str(customer.user_id) != str(user_id):
            logger.warning(f"⛔ Access denied: user_id={user_id} does not own customer_id={customer_id} (DB owner: {customer.user_id})")
            return jsonify({"error": "Access denied"}), 403

        orders = Payments.query.filter_by(customer_id=customer_id).all()
        logger.debug(f"✅ Found {len(orders)} order(s) for customer_id={customer_id}")

        return jsonify({
            "orders": [order.to_dict() for order in orders],
            "message": "ยังไม่มีคำสั่งซื้อ" if not orders else "คำสั่งซื้อถูกดึงสำเร็จ"
        }), 200

    except Exception as e:
        logger.exception(f"❌ Unexpected error while checking orders for customer_id={customer_id}")
        return jsonify({"error": "An error occurred while fetching orders"}), 500
