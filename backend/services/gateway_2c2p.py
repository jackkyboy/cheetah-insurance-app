#/Users/apichet/Downloads/cheetah-insurance-app/backend/services/gateway_2c2p.py
import os
import uuid
import requests
import logging
from backend.services.token_service import generate_token as create_jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Gateway2C2P:
    def __init__(self):
        self.api_url = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/")
        self.secret_key = os.getenv("MERCHANT_SECRET")
        if not self.secret_key:
            raise ValueError("❌ Missing Merchant Secret Key")
        logger.info("✅ Gateway2C2P initialized successfully.")

    @staticmethod
    def send_post_request(api_url, payload, retries=3):
        """
        Utility function to send HTTP POST requests with retry logic.
        """
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        for attempt in range(retries):
            try:
                logger.debug(f"🔧 Sending POST request to {api_url} with payload: {payload}")
                response = requests.post(api_url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                logger.debug(f"✅ Response: {response.json()}")
                return response.json()
            except requests.Timeout:
                logger.error(f"❌ HTTP request timed out. Attempt {attempt + 1} of {retries}")
                if attempt == retries - 1:
                    raise
            except requests.RequestException as e:
                logger.error(f"❌ HTTP request error: {e}. Attempt {attempt + 1} of {retries}")
                if attempt == retries - 1:
                    raise

    @staticmethod
    def get_merchant_config(country_code="TH"):
        """
        Retrieve merchant configuration based on the country code.
        """
        try:
            merchant_id = os.getenv(f"MERCHANT_CONFIG_{country_code}_ID")
            secret_key = os.getenv(f"MERCHANT_CONFIG_{country_code}_SECRET")
            currency_code = os.getenv(f"MERCHANT_CONFIG_{country_code}_CURRENCY", "THB")

            if not merchant_id or not secret_key:
                raise ValueError(f"❌ Missing Merchant Config for {country_code}")
            logger.debug(f"✅ Merchant Config: {merchant_id}, Currency: {currency_code}")
            return {"merchant_id": merchant_id, "secret_key": secret_key, "currency_code": currency_code}
        except ValueError as ve:
            logger.error(ve)
            raise

    @staticmethod
    def create_payment_token(invoice_no, amount, description="Purchase", country_code="TH"):
        """
        Creates a payment token for processing payments.
        """
        try:
            config = Gateway2C2P.get_merchant_config(country_code)
            formatted_amount = f"{float(amount):012.5f}"  # Format amount to 12-digit with 5 decimals
            payload = {
                "merchantID": config["merchant_id"],
                "invoiceNo": invoice_no,
                "description": description,
                "amount": formatted_amount,
                "currencyCode": config["currency_code"],
                "tokenize": True,
                "request3DS": "Y",
                "idempotencyID": str(uuid.uuid4()),
            }

            logger.debug(f"🔧 Payload for Payment Token: {payload}")

            token = create_jwt(payload, config["secret_key"])
            if not token:
                raise ValueError("❌ Failed to create JWT token")

            api_url = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentToken")
            response = Gateway2C2P.send_post_request(api_url, {"payload": token})
            logger.debug(f"✅ Payment Token Response: {response}")
            return response
        except Exception as e:
            logger.error(f"❌ Error creating payment token: {e}")
            raise

    @staticmethod
    def fetch_payment_options(payment_token):
        """
        Fetches available payment options for the given payment token.
        """
        try:
            payload = {"paymentToken": payment_token, "locale": "en", "clientID": os.getenv("CLIENT_ID")}
            api_url = os.getenv("SANDBOX_API_FETCH_OPTIONS", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentOption")
            logger.debug(f"🔧 Fetching payment options with payload: {payload}")
            response = Gateway2C2P.send_post_request(api_url, payload)
            logger.debug(f"✅ Payment Options Response: {response}")
            return response
        except Exception as e:
            logger.error(f"❌ Error fetching payment options: {e}")
            raise

    @staticmethod
    def do_payment(payment_token, client_ip, payment_data):
        """
        Processes the payment using the given payment token.
        """
        try:
            # Set endpoint URL (ensure it's correct)
            api_url = os.getenv("SANDBOX_API_DO_PAYMENT", "https://sandbox-pgw.2c2p.com/payment/4.3/doPayment")
            logger.debug(f"🔧 Using payment endpoint: {api_url}")

            # Prepare payload
            payload = {
                "paymentToken": payment_token,
                "locale": "en",
                "clientIP": client_ip,
                "payment": payment_data,
            }
            logger.debug(f"🔧 Sending payment payload: {payload}")

            # Send POST request
            response = Gateway2C2P.send_post_request(api_url, payload)
            logger.debug(f"✅ Payment Gateway Response: {response}")

            return response

        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error in do_payment: {e}")
            raise



