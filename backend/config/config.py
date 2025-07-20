# /Users/apichet/Downloads/cheetah-insurance-app/backend/config/config.py
# /backend/config/config.py
import os
import base64
from dotenv import load_dotenv

# === 🌐 ENVIRONMENT LOADING ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DOTENV_PATH = {
    "production": ".env.production",
    "development": ".env",
    "sandbox": ".env"
}.get(ENVIRONMENT, ".env")

if os.path.exists(DOTENV_PATH):
    load_dotenv(DOTENV_PATH)

# === 🔐 BASE64 SECRET FILES DECODER ===
def decode_base64_env_files():
    output_paths = {
        "SANDBOX_PKCS7_BASE64": "/tmp/sandbox-pkcs7.cer",
        "PRIVATE_KEY_BASE64": "/tmp/merchant-private-key.der",
        "PUBLIC_CERT_BASE64": "/tmp/jwt-demo.cer",
        "GOOGLE_CREDENTIALS_BASE64": "/tmp/credentials.json"
    }

    for var, filepath in output_paths.items():
        val = os.getenv(var)
        if val:
            try:
                with open(filepath, "wb") as f:
                    f.write(base64.b64decode(val))
                print(f"✅ Decoded {var} → {filepath}")
            except Exception as e:
                print(f"❌ Failed to decode {var}: {e}")
        else:
            print(f"⚠️ Missing env variable: {var}")

    # Set default GOOGLE_APPLICATION_CREDENTIALS if decoded
    if os.getenv("GOOGLE_CREDENTIALS_BASE64"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/credentials.json"

decode_base64_env_files()

# === ⚙️ MAIN CONFIGURATION CLASS ===
class Config:
    # --- General ---
    ENVIRONMENT = os.getenv("ENVIRONMENT", "sandbox")
    SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "fallback_flask_secret_key"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

    # --- JWT ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_jwt_secret_key")
    ACCESS_TOKEN_EXPIRY_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRY_HOURS", 24))
    REFRESH_TOKEN_EXPIRY_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRY_DAYS", 7))
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = ACCESS_TOKEN_EXPIRY_HOURS * 3600
    JWT_REFRESH_TOKEN_EXPIRES = REFRESH_TOKEN_EXPIRY_DAYS * 86400
    JWT_BLACKLIST_ENABLED = os.getenv("JWT_BLACKLIST_ENABLED", "True") == "True"

    # --- Frontend URLs ---
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
    FRONTEND_RETURN_URL = os.getenv("FRONTEND_RETURN_URL", f"{FRONTEND_URL}/success")
    BACKEND_RETURN_URL = os.getenv("BACKEND_RETURN_URL", "http://127.0.0.1:5000/api/payment_callback")

    # --- CORS ---
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", ",".join([
        "http://localhost:3001",
        "https://cheetahinsurancebroker.com",
        "https://app.cheetahinsurancebroker.com",
        "https://63894e1bb428.ngrok-free.app"
    ])).split(",")

    # --- Database ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
    INSTANCE_DIR = os.path.join(PROJECT_ROOT, "instance")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", f"sqlite:///{os.path.join(INSTANCE_DIR, 'cheetah_insurance.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Uploads ---
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))

    # --- Payment Gateway URLs ---
    SANDBOX_API_URL = os.getenv("SANDBOX_API_URL", "https://sandbox-pgw.2c2p.com/payment/4.3/paymentToken")
    PRODUCTION_API_URL = os.getenv("PRODUCTION_API_URL", "https://pgw.2c2p.com/payment/4.3/paymentToken")

    @staticmethod
    def get_api_url():
        return Config.PRODUCTION_API_URL if Config.ENVIRONMENT == "production" else Config.SANDBOX_API_URL

    # --- Email ---
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # --- Merchant Info ---
    MERCHANT_CONFIG_TH_ID = os.getenv("MERCHANT_CONFIG_TH_ID", "default_merchant_id")
    MERCHANT_CONFIG_TH_SECRET = os.getenv("MERCHANT_CONFIG_TH_SECRET", "default_merchant_secret")
    MERCHANT_CONFIG_TH_CURRENCY = os.getenv("MERCHANT_CONFIG_TH_CURRENCY", "THB")

    # --- Certificate Paths ---
    CERT_PATH = os.getenv("CERT_PATH", "/tmp/sandbox-pkcs7.cer")
    PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", "/tmp/jwt-demo.cer")
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/tmp/merchant-private-key.der")

    # --- Logger Preview ---
    @staticmethod
    def log_configuration():
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(Config.LOG_LEVEL)
        logger.debug("🔧 CONFIGURATION SETTINGS")
        for attr in dir(Config):
            if attr.isupper():
                logger.debug(f"{attr}: {getattr(Config, attr)}")

# 🧪 CLI DEBUG MODE
if __name__ == "__main__":
    Config.log_configuration()
