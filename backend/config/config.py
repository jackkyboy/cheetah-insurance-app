# /Users/apichet/Downloads/cheetah-insurance-app/backend/config/config.py
import os
from dotenv import load_dotenv


# ✅ โหลดตัวแปรจากไฟล์ .env (หากมี)
if os.path.exists(".env"):
    load_dotenv()

class Config:
    # --- Environment Configuration ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")  # Default to sandbox
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "fallback_flask_secret_key")
    SECRET_KEY = os.getenv("SECRET_KEY", FLASK_SECRET_KEY)  # Single consistent SECRET_KEY
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    GOOGLE_APPLICATION_CREDENTIALS = "backend/config/credentials.json"
    
    # --- Token Expiry Configuration ---
    ACCESS_TOKEN_EXPIRY_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRY_HOURS", 24))  # Access token expiry in hours
    REFRESH_TOKEN_EXPIRY_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", 7))  # Refresh token expiry in days

    # --- SMTP Email Configuration ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # --- JWT Configuration ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_jwt_secret_key")  # Use specific fallback for JWT
    JWT_TOKEN_LOCATION = ["headers", "cookies"]  # Allow headers or cookies for JWT
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_TOKEN_EXPIRY_HOURS * 3600  # Convert hours to seconds
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_TOKEN_EXPIRY_DAYS * 86400  # Convert days to seconds
    JWT_BLACKLIST_ENABLED = os.getenv("JWT_BLACKLIST_ENABLED", "True") == "True"

    # --- CORS Configuration ---
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")

    # --- Database Configuration ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
    DATABASE_URI = os.getenv(
        "DATABASE_URI", f"sqlite:///{os.path.join(INSTANCE_DIR, 'cheetah_insurance.db')}"
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable SQLAlchemy modification tracking

    # --- File Upload Configuration ---
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))

    # --- Payment API URLs ---
    SANDBOX_API_URL = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentToken")
    PRODUCTION_API_URL = os.getenv("PRODUCTION_API_URL", "https://pgw.2c2p.com/payment/4.3/paymentToken")
    
    # --- Return URLs ---
    FRONTEND_RETURN_URL = os.getenv("FRONTEND_RETURN_URL", "http://localhost:3000/success")
    BACKEND_RETURN_URL = os.getenv("BACKEND_RETURN_URL", "http://127.0.0.1:5000/api/payment_callback")

    # --- Logging Configuration ---
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

    # --- Merchant Configuration ---
    MERCHANT_CONFIG_TH_ID = os.getenv("MERCHANT_CONFIG_TH_ID", "default_merchant_id")
    MERCHANT_CONFIG_TH_SECRET = os.getenv("MERCHANT_CONFIG_TH_SECRET", "default_merchant_secret")
    MERCHANT_CONFIG_TH_CURRENCY = os.getenv("MERCHANT_CONFIG_TH_CURRENCY", "THB")

    # --- Certificate Paths ---
    CERT_PATH = os.getenv("CERT_PATH", os.path.join("certs", "cert.cer"))
    PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", os.path.join("certs", "public-key.cer"))
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", os.path.join("certs", "merchant-private-key.der"))

    # --- Helper Methods ---
    @staticmethod
    def get_api_url():
        """Returns the appropriate API URL based on the environment."""
        return Config.PRODUCTION_API_URL if Config.ENVIRONMENT == "production" else Config.SANDBOX_API_URL

    @staticmethod
    def log_configuration():
        """Debugging method to log all configuration values."""
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(Config.LOG_LEVEL)

        logger.debug("🔧 [CONFIGURATION SETTINGS]")
        logger.debug(f"ENVIRONMENT: {Config.ENVIRONMENT}")
        logger.debug(f"SECRET_KEY: {Config.SECRET_KEY}")
        logger.debug(f"JWT_SECRET_KEY: {Config.JWT_SECRET_KEY}")
        logger.debug(f"JWT_ACCESS_TOKEN_EXPIRES: {Config.JWT_ACCESS_TOKEN_EXPIRES}")
        logger.debug(f"JWT_REFRESH_TOKEN_EXPIRES: {Config.JWT_REFRESH_TOKEN_EXPIRES}")
        logger.debug(f"DATABASE_URI: {Config.SQLALCHEMY_DATABASE_URI}")
        logger.debug(f"UPLOAD_DIR: {Config.UPLOAD_DIR}")
        logger.debug(f"MERCHANT_CONFIG_TH_ID: {Config.MERCHANT_CONFIG_TH_ID}")
        logger.debug(f"MERCHANT_CONFIG_TH_SECRET: {Config.MERCHANT_CONFIG_TH_SECRET}")
        logger.debug(f"MERCHANT_CONFIG_TH_CURRENCY: {Config.MERCHANT_CONFIG_TH_CURRENCY}")
        logger.debug(f"CERT_PATH: {Config.CERT_PATH}")
        logger.debug(f"PUBLIC_KEY_PATH: {Config.PUBLIC_KEY_PATH}")
        logger.debug(f"PRIVATE_KEY_PATH: {Config.PRIVATE_KEY_PATH}")

# ✅ Debugging Configurations (Optional)
if __name__ == "__main__":
    Config.log_configuration()
