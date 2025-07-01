# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
# /Users/apichet/Downloads/cheetah-insurance-app/services/payment_service.py
import os
import uuid
import urllib.parse
import logging
from datetime import datetime
import requests
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

class PaymentService:
    @staticmethod
    def create_payment_order(customer_id, package_data):
        """
        Creates a new payment order.

        Args:
            customer_id (int): ID of the customer.
            package_data (dict): Additional payment details.

        Returns:
            dict: A dictionary representation of the created payment.
        """
        try:
            logger.debug(f"🚀 Starting to create payment order. Customer ID: {customer_id}, Package Data: {package_data}")

            # Validate customer_id
            if not customer_id:
                logger.warning("⚠️ Customer ID is missing.")
                raise ValueError("❌ Customer ID is required.")

            # Generate order_id
            order_id = str(uuid.uuid4())
            logger.debug(f"🔧 Generated order ID: {order_id} for customer_id={customer_id}")

            # Extract and validate amount
            amount = package_data.get("amount", 0)
            if amount <= 0:
                logger.warning(f"⚠️ Invalid amount: {amount} for order_id={order_id}")
                raise ValueError("❌ Amount must be greater than 0.")

            # Validate package_id (can be null but must be an integer if provided)
            package_id = package_data.get("package_id")
            if package_id is not None and not isinstance(package_id, int):
                logger.warning(f"⚠️ Invalid package ID: {package_id} for order_id={order_id}")
                raise ValueError("❌ Package ID must be an integer or null.")

            # Handle add_ons as a comma-separated string
            add_ons = package_data.get("add_ons", [])
            if not isinstance(add_ons, list):
                logger.warning(f"⚠️ Invalid add-ons format: {add_ons} for order_id={order_id}")
                raise ValueError("❌ Add-ons must be a list.")
            add_ons_str = ",".join(map(str, add_ons))  # Convert list to comma-separated string
            logger.debug(f"🛠️ Add-ons processed for order_id={order_id}: {add_ons_str}")

            # Log details of the payment being created
            logger.debug(f"📋 Payment Details - Amount: {amount}, Package ID: {package_id}, Add-ons: {add_ons_str}")

            # Create payment order
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

            # Save to database
            db.session.add(payment)
            db.session.commit()

            logger.info(f"✅ Payment order created successfully: {order_id}")
            return payment.to_dict()

        except ValueError as ve:
            logger.error(f"❌ Validation error for customer_id={customer_id}: {ve}")
            raise ve
        except Exception as e:
            db.session.rollback()
            logger.exception(f"❌ Error creating payment order for customer_id={customer_id}: {str(e)}")
            raise Exception(f"Error creating payment order: {str(e)}")


    @staticmethod
    def create_payment_token(invoice_no, amount, description="Payment", country_code="TH", user_id=None, role=None):
        """
        Generates a payment token for 2C2P.

        Args:
            invoice_no (str): Unique invoice number for the transaction.
            amount (float): Transaction amount.
            description (str, optional): Payment description. Defaults to "Payment".
            country_code (str, optional): Country code for the transaction. Defaults to "TH".
            user_id (int): ID of the user initiating the payment.
            role (str, optional): User role ("user" or "admin"). Defaults to "user".

        Returns:
            dict: Response from the 2C2P API containing the payment token.
        """
        logger.debug("🔧 Generating payment token...")
        try:
            # Validate required environment variables
            merchant_id = os.getenv("MERCHANT_CONFIG_TH_ID")
            secret_key = os.getenv("MERCHANT_CONFIG_TH_SECRET")
            api_url = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentToken")

            if not merchant_id or not secret_key:
                logger.error("❌ Missing environment variables: MERCHANT_CONFIG_TH_ID or MERCHANT_CONFIG_TH_SECRET.")
                raise EnvironmentError("Merchant ID and Secret Key are required for generating payment tokens.")

            # Validate required arguments
            if not user_id:
                raise ValueError("❌ User ID is required for JWT generation.")
            if not invoice_no:
                raise ValueError("❌ Invoice number is required.")
            if role and role not in ["user", "admin"]:
                raise ValueError(f"❌ Invalid role: {role}. Allowed values are 'user' or 'admin'.")

            # Set default role if not provided
            role = role or "user"

            # Format amount to two decimal places
            formatted_amount = f"{float(amount):.2f}"

            # Build payload for JWT
            payload = {
                "merchantID": merchant_id,
                "invoiceNo": invoice_no,
                "amount": formatted_amount,
                "currencyCode": "THB",
                "description": description,
                "countryCode": country_code,
                "user_id": user_id,
                "role": role,  # Include role in payload
            }

            logger.debug(f"🔑 JWT Payload: {payload}")

            # Generate JWT token
            jwt_token = generate_jwt(payload, secret_key)
            logger.debug(f"✅ Generated JWT token: {jwt_token}")

            # Prepare API request
            headers = {"Content-Type": "application/json"}
            api_payload = {"payload": jwt_token}

            logger.info("📡 Sending request to 2C2P API...")
            response = requests.post(api_url, json=api_payload, headers=headers)

            # Log response status and body
            logger.debug(f"Response Status: {response.status_code}")
            logger.debug(f"Response Body: {response.text}")

            # Raise an error for non-2xx HTTP statuses
            response.raise_for_status()

            logger.info("✅ Payment token generated successfully.")
            return response.json()

        except requests.exceptions.RequestException as req_err:
            logger.error(f"❌ Request error with 2C2P API: {req_err}")
            raise Exception("Failed to communicate with 2C2P API.") from req_err

        except ValueError as val_err:
            logger.error(f"❌ Validation error: {val_err}")
            raise val_err

        except EnvironmentError as env_err:
            logger.error(f"❌ Environment configuration error: {env_err}")
            raise env_err

        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise Exception("An unexpected error occurred during payment processing.") from e

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
