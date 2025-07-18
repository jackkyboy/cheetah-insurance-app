# /Users/apichet/Downloads/cheetah-insurance-app/backend/__init__.py
import os
import logging
from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS

from backend.models import db, initialize_models
from backend.routes import register_blueprints
from backend.routes.multi_step_search import set_app_instance
from backend.services.bigquery_service import BigQueryService
from backend.config.config import Config
from backend.extensions import cache

# === Logging Setup ===
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    configure_database(app)
    configure_cache(app)
    configure_cors(app)
    configure_bigquery(app)
    register_routes(app)

    register_after_request_handler(app)

    return app

def configure_database(app):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "instance", "cheetah_insurance.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        try:
            db.create_all()
            logger.debug("✅ DB tables created.")
        except Exception as e:
            logger.error(f"❌ DB creation failed: {e}")
            raise

        try:
            initialize_models()
            logger.debug("✅ Models initialized.")
        except Exception as e:
            logger.error(f"❌ Model init failed: {e}")
            raise

def configure_cache(app):
    cache.init_app(app)
    app.extensions.setdefault("cache", {})["default"] = cache
    logger.debug("✅ Cache bound to app.extensions['cache']")

def configure_bigquery(app):
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cheetah-insurance-broker")
        bq_service = BigQueryService(project_id=project_id, location="asia-southeast1")
        app.extensions["bigquery_service"] = bq_service
        logger.info(f"✅ BigQueryService injected: {project_id}")
    except Exception as e:
        logger.critical(f"❌ BigQueryService init failed: {e}")
        raise

def configure_cors(app):
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "https://cheetahinsurancebroker.com",
                "https://app.cheetahinsurancebroker.com",
                "https://63894e1bb428.ngrok-free.app"
            ],
            "supports_credentials": True
        }
    }, supports_credentials=True)

def register_routes(app):
    try:
        set_app_instance(app)
        register_blueprints(app)
        logger.info("✅ Blueprints registered.")
    except Exception as e:
        logger.error(f"❌ Blueprint registration failed: {e}")
        raise

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {"status": "ok"}, 200
    


def register_after_request_handler(app):
    @app.after_request
    def after_request_cors(response):
        origin = request.headers.get("Origin")
        allowed_origins = app.config.get("CORS_ALLOWED_ORIGINS", [])

        if origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin  # ✅ Only one origin
            response.headers["Vary"] = "Origin"  # ✅ Recommend for caching

        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response
