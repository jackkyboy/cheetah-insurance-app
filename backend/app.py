# /Users/apichet/Downloads/cheetah-insurance-app/backend/app.py
# backend/app.py
# backend/app.py
import os
import logging
from flask import Flask, jsonify, current_app, request, send_from_directory
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from backend.config.config import Config
from backend.db import db
from backend.extensions import cache
from backend.models import initialize_models, init_app
from backend.routes import register_blueprints, configure_app
from backend.services.bigquery_service import BigQueryService
from backend.utils import decode_secrets
import pymysql

# === Logger Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

jwt = JWTManager()
pymysql.install_as_MySQLdb()


def create_app():
    # === Decode Base64 .env Secrets ===
    secrets = {
        "SANDBOX_PKCS7_BASE64": "/tmp/sandbox-pkcs7.cer",
        "PRIVATE_KEY_BASE64": "/tmp/merchant-private-key.der",
        "PUBLIC_CERT_BASE64": "/tmp/jwt-demo.cer",
        "GOOGLE_CREDENTIALS_BASE64": "/tmp/credentials.json"
    }
    for env_key, file_path in secrets.items():
        decode_secrets.decode_env_to_file(env_key, file_path)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = secrets["GOOGLE_CREDENTIALS_BASE64"]

    # === Initialize Flask App ===
    app_root = os.path.abspath(os.path.dirname(__file__))
    frontend_build_path = os.path.join(app_root, "build")
    static_path = os.path.join(frontend_build_path, "static")

    app = Flask(__name__, static_folder=static_path, static_url_path="/static")
    app.config.from_object(Config)

    logger.info(f"🚀 Starting Flask app with build folder: {frontend_build_path}")
    logger.info(f"📁 Static files served from: {static_path}")

    # === Register System ===
    init_extensions(app)
    configure_app(app)
    register_blueprints(app)
    setup_spa_routes(app, frontend_build_path)
    setup_jwt_error_handlers(jwt)
    setup_cli_utilities(app)
    register_services(app)

    return app


def init_extensions(app):
    cache.init_app(app)
    app.extensions.setdefault("cache", {})["default"] = cache

    allowed_origins = Config.CORS_ALLOWED_ORIGINS.split(",")
    CORS(app, origins=allowed_origins, supports_credentials=True)
    app.after_request(lambda response: add_cors_headers(response, allowed_origins))

    jwt.init_app(app)
    init_app(app)
    Migrate(app, db)


def add_cors_headers(response, allowed_origins):
    origin = request.headers.get("Origin")
    if origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


def setup_spa_routes(app, build_path):
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_spa(path):
        full_path = os.path.join(build_path, path)
        if path != "" and os.path.exists(full_path):
            return send_from_directory(build_path, path)
        return send_from_directory(build_path, "index.html")


def register_services(app):
    with app.app_context():
        try:
            initialize_models()
            logger.info("✅ Models initialized.")
        except Exception as e:
            logger.error(f"❌ Model init failed: {e}")
            raise

        try:
            app.extensions["bigquery_service"] = BigQueryService()
            logger.info("✅ BigQueryService registered.")
        except Exception as e:
            logger.error(f"❌ BigQueryService error: {e}")


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


# 👇 Allow Gunicorn / Railway to access app
app = create_app()

if __name__ == "__main__":
    try:
        print("\n📦 Registered Routes:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            print(f"➡️ {rule} [{methods}]")
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"❌ Error starting Flask app: {e}")
        raise
