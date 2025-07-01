# /Users/apichet/Downloads/cheetah-insurance-app/backend/app.py
import os
import sys
import logging
from flask import Flask, jsonify, current_app
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_caching import Cache

from backend.config.config import Config
from backend.models import db, initialize_models, init_app
from backend.routes import register_blueprints, configure_app  # ✅ ใช้ configure_app จาก routes
from backend.config.bigquery_config import BigQueryConfig

# === Logger ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300})
jwt = JWTManager()


def initialize_credentials():
    credentials_path = os.path.join(os.path.dirname(__file__), "config/credentials.json")
    if not os.path.exists(credentials_path):
        logger.error(f"❌ Credentials file not found at {credentials_path}.")
        sys.exit(1)
    os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", credentials_path)
    logger.info(f"✅ GOOGLE_APPLICATION_CREDENTIALS set to {credentials_path}")


def create_app():
    initialize_credentials()

    app = Flask(__name__, static_folder="../build", static_url_path="")
    app.config.from_object(Config)
    logger.info("🚀 Starting Flask application...")

    # === Init Core Services ===
    cache.init_app(app)
    app.extensions.setdefault("cache", {})["default"] = cache
    app.extensions["cache"][cache] = cache

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    init_app(app)
    Migrate(app, db)
    jwt.init_app(app)

    # === Load Services from backend.routes ===
    configure_app(app)
    register_blueprints(app)

    # === Attach Handlers ===
    setup_jwt_error_handlers(jwt)
    setup_cli_utilities(app)
    app.after_request(after_request_cors)

    # === Runtime Init ===
    with app.app_context():
        try:
            initialize_models()
            logger.info("✅ Models initialized.")
        except Exception as e:
            logger.error(f"❌ Model init failed: {e}")
            raise

        try:
            bq_config = BigQueryConfig()
            app.extensions["bigquery_config"] = bq_config
            logger.info("✅ BigQueryConfig registered.")
        except Exception as e:
            logger.error(f"❌ BigQueryConfig error: {e}")

    return app


def after_request_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


def setup_jwt_error_handlers(jwt):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Token is missing"}), 401

    @jwt.needs_fresh_token_loader
    def needs_fresh_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Fresh token required"}), 401


def setup_cli_utilities(app):
    @app.cli.command("list-routes")
    def list_routes():
        print(f"{'Method':<10} {'Endpoint':<50} {'Function':<50}")
        print("=" * 110)
        for rule in current_app.url_map.iter_rules():
            methods = ",".join(rule.methods)
            endpoint = rule.endpoint
            function = current_app.view_functions[rule.endpoint].__name__
            print(f"{methods:<10} {str(rule):<50} {function:<50}")



if __name__ == "__main__":
    try:
        app = create_app()

        # 🔍 Debug Routes
        print("\n📦 Registered Routes:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            print(f"➡️ {rule} [{methods}]")

        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"❌ Error starting Flask app: {e}")
        raise
