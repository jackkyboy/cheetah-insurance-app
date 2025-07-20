# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
import os
import uuid
import urllib.parse
import logging
from datetime import datetime, timedelta
import requests
import jwt
from flask import Flask
from flask_cors import CORS
from backend.models.Payments import Payments
from backend import db
from backend.config.config import Config
from backend.utils.jwt_utils import generate_jwt
from backend.models import db




# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def validate_payment_environment():
        """
        Validates required environment variables for payment processing.
        """
        required_envs = [
            "MERCHANT_CONFIG_TH_ID",
            "MERCHANT_CONFIG_TH_SECRET",
            "SANDBOX_API_URL",
            "SANDBOX_SECURE_PAYMENT_3DS_URL",
            "BACKEND_RETURN_URL",
        ]
        for env in required_envs:
            if not os.getenv(env):
                raise ValueError(f"❌ Missing required environment variable: {env}")
        logger.info("✅ All required environment variables are set.")

    @staticmethod
    def create_payment_order(customer_id, package_data):
        """
        Creates a new payment order with a formatted invoice_no instead of UUID.
        """
        def validate_input():
            if not customer_id:
                raise ValueError("❌ Customer ID is required.")

            if not isinstance(package_data, dict):
                raise ValueError("❌ Package data must be a dictionary.")

            amount = package_data.get("amount", 0)
            if amount <= 0:
                raise ValueError("❌ Amount must be greater than 0.")

            package_id = package_data.get("package_id")
            if package_id is not None and not isinstance(package_id, (str, int)):
                raise ValueError("❌ Package ID must be a string or integer.")

            add_ons = package_data.get("add_ons", [])
            if not isinstance(add_ons, list):
                raise ValueError("❌ Add-ons must be a list.")

            return amount, package_id, ",".join(map(str, add_ons))

        try:
            logger.debug(f"🚀 Creating payment order | customer_id={customer_id} | package_data={package_data}")

            # ✅ Input validation
            amount, package_id, add_ons_str = validate_input()

            # ✅ Generate formatted invoice_no (useful as order_id)
            order_id = f"INV{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            logger.debug(f"🔧 Generated order_id={order_id}")

            # ✅ Build payment object
            payment = Payments(
                order_id=order_id,
                customer_id=customer_id,
                package_id=package_id,
                amount=amount,
                premium=package_data.get("premium", 0),
                duty=package_data.get("duty", 0),
                vat=package_data.get("vat", 0),
                total_price=package_data.get("total_price", amount),
                add_ons=add_ons_str,
                coupon_code=package_data.get("coupon_code"),
                coverage_start_date=package_data.get("coverage_start_date"),
                coverage_start_time=package_data.get("coverage_start_time"),
                insurance_company=package_data.get("insurance_company"),
                insurance_type=package_data.get("insurance_type"),
                car_brand=package_data.get("car_brand"),
                car_model=package_data.get("car_model"),
                car_submodel=package_data.get("car_submodel"),
                car_year=package_data.get("car_year"),
                payment_status="pending",
            )

            db.session.add(payment)
            db.session.commit()

            logger.info(f"✅ Payment order created | order_id={order_id}")
            return payment.to_dict()

        except ValueError as ve:
            logger.error(f"❌ Validation error | customer_id={customer_id} | {ve}")
            raise ve
        except Exception as e:
            db.session.rollback()
            logger.exception(f"❌ Unexpected error during payment order creation | customer_id={customer_id}")
            raise Exception(f"Error creating payment order: {str(e)}")





    @staticmethod
    def create_payment_token(invoice_no, amount, description="Payment", country_code="TH", user_id=None, role=None):
        """
        Generates a payment token for 2C2P and wraps it in a JWT for frontend use.
        """
        logger.debug("🔧 Generating payment token...")
        try:
            # ✅ Load environment variables
            merchant_id = os.getenv("MERCHANT_CONFIG_TH_ID")
            secret_key_2c2p = os.getenv("MERCHANT_CONFIG_TH_SECRET")
            jwt_secret = os.getenv("JWT_SECRET_KEY")
            api_url = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentToken")

            if not merchant_id or not secret_key_2c2p:
                raise EnvironmentError("❌ Missing 2C2P merchant credentials.")

            if not jwt_secret:
                raise EnvironmentError("❌ JWT_SECRET_KEY is required.")

            if not user_id:
                raise ValueError("❌ User ID is required.")

            if not invoice_no:
                raise ValueError("❌ Invoice number is required.")

            if role and role not in ["user", "admin"]:
                raise ValueError("❌ Invalid role.")
            role = role or "user"

            formatted_amount = f"{float(amount):.2f}"

            # ✅ Prepare payload for 2C2P
            payload_2c2p = {
                "merchantID": merchant_id,
                "invoiceNo": invoice_no,
                "amount": formatted_amount,
                "currencyCode": "THB",
                "description": description,
                "countryCode": country_code,
                "user_id": user_id,
                "role": role,
            }

            logger.debug(f"🔑 JWT Payload to 2C2P: {payload_2c2p}")
            jwt_token = generate_jwt(payload_2c2p, secret_key_2c2p)

            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, json={"payload": jwt_token}, headers=headers)

            logger.debug(f"📨 2C2P Response Status: {response.status_code}")
            logger.debug(f"📨 2C2P Response Body: {response.text}")
            response.raise_for_status()

            # ✅ Step 1: Extract payload from 2C2P's JWT response
            result = response.json()
            jwt_encoded = result.get("payload")
            if not jwt_encoded:
                raise Exception("2C2P response missing 'payload' field.")

            # ✅ Step 2: Decode JWT (don't verify signature)
            try:
                decoded = jwt.decode(jwt_encoded, options={"verify_signature": False})
                logger.debug(f"🔓 Decoded 2C2P JWT: {decoded}")
            except Exception as decode_err:
                raise Exception("Failed to decode 2C2P JWT") from decode_err

            payment_token = decoded.get("paymentToken")
            web_payment_url = decoded.get("webPaymentUrl")
            resp_code = decoded.get("respCode", "9999")

            if not payment_token or not web_payment_url:
                raise Exception("Invalid 2C2P payload: missing paymentToken or webPaymentUrl")

            # ✅ Step 3: Generate final JWT for frontend
            # ✅ Step 3: Generate final JWT for frontend
            now = datetime.utcnow()
            final_payload = {
                "paymentToken": payment_token,
                "webPaymentUrl": web_payment_url,
                "respCode": resp_code,
                "invoiceNo": invoice_no,
                "amount": formatted_amount,
                "user_id": user_id,
                "role": role,
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=15)).timestamp()),
            }

            final_jwt = jwt.encode(final_payload, jwt_secret, algorithm="HS256")

            # ✅ FIX: Convert bytes to string if needed
            if isinstance(final_jwt, bytes):
                final_jwt = final_jwt.decode("utf-8")

            logger.debug(f"🎁 Final JWT to frontend: {final_jwt}")
            return {"payload": final_jwt}


        except Exception as e:
            logger.exception("❌ Error during create_payment_token:")
            raise

            

    @staticmethod
    def get_payment_order(order_id):
        """
        Fetch a payment order using the order_id (UUID).

        Args:
            order_id (str): The unique order ID.

        Returns:
            dict: A dictionary representation of the payment order or None if not found.
        """
        try:
            logger.debug(f"🔍 Searching for payment with order_id={order_id}")
            payment = Payments.query.filter_by(order_id=order_id).first()
            if not payment:
                logger.warning(f"⚠️ No payment found for order_id={order_id}")
                return None
            logger.info(f"✅ Payment order found: {order_id}")
            return payment.to_dict()
        except Exception as e:
            logger.error(f"❌ Error fetching payment order: {e}", exc_info=True)
            return None


    @staticmethod
    def generate_2c2p_payment_url(payment):
        """
        Generates a redirect URL for 2C2P payment gateway.

        Args:
            payment (Payments): The payment object.

        Returns:
            str: The redirect URL to the payment gateway.
        """
        try:
            base_url = "https://payment.2c2p.com/payment"
            params = {
                'order_id': payment.order_id,
                'amount': f"{payment.amount:.2f}",
                'currency': payment.currency,
                'redirect_url': "https://your-website.com/payment/callback",  # Replace with actual redirect URL
                'merchant_id': "YOUR_MERCHANT_ID"  # Replace with your 2C2P merchant ID
            }
            query_string = urllib.parse.urlencode(params)
            payment_url = f"{base_url}?{query_string}"
            logger.info(f"✅ Generated 2C2P payment URL: {payment_url}")
            return payment_url
        except Exception as e:
            logger.exception("❌ Error generating 2C2P payment URL.")
            raise Exception(f"Error generating payment URL: {str(e)}")

# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py

    @staticmethod
    def get_payment_order_by_invoice(invoice_no):
        """
        Fetch a payment order using the invoice number.

        Args:
            invoice_no (str): The invoice number to search for.

        Returns:
            Payments: The payment order object if found, else None.
        """
        try:
            payment_order = Payments.query.filter_by(order_id=invoice_no).first()
            if payment_order:
                return payment_order
            else:
                return None
        except Exception as e:
            # Log exception for debugging
            logger.error(f"❌ Error fetching payment order by invoice_no: {invoice_no}. Error: {str(e)}")
            return None


    @staticmethod
    def get_payment_order_status(invoice_no):
        """
        Fetch the status of a payment order using the invoice number.
        Args:
            invoice_no (str): Invoice number of the payment order.
        Returns:
            dict: Payment order details or None if not found.
        """
        try:
            payment_order = Payments.query.filter_by(order_id=invoice_no).first()
            if not payment_order:
                return None
            return payment_order.to_dict()
        except Exception as e:
            logging.error(f"❌ Error fetching payment order by invoice: {str(e)}")
            return None
        

    @staticmethod
    def update_payment_status(order_id, status):
        """
        Update the payment status for the given order ID.
        """
        try:
            logger.debug(f"🔍 Searching for payment order with order_id={order_id}")

            payment = Payments.query.filter_by(order_id=order_id).first()
            if not payment:
                logger.warning(f"❌ No payment found with order_id={order_id}")
                return False

            logger.info(f"🛠️ Updating payment status to {status} for order_id={order_id}")
            payment.payment_status = status
            payment.updated_at = datetime.utcnow()  # Ensure datetime is imported

            db.session.commit()
            logger.info(f"✅ Payment status updated successfully for order_id={order_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating payment status: {str(e)}", exc_info=True)
            db.session.rollback()
            raise e
