# /Users/apichet/Downloads/cheetah-insurance-app/backend/__init__.py
import os
import logging
from flask import Flask
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

# === Init Flask App ===
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)

# === Enable CORS ===
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# === SQLite DB Config (local dev only) ===
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "instance", "cheetah_insurance.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

# === Init DB + Migrate ===
db.init_app(app)
Migrate(app, db)

# === Init Cache ===
cache.init_app(app)
if "cache" not in app.extensions:
    app.extensions["cache"] = {}
app.extensions["cache"]["default"] = cache
app.extensions["cache"][cache] = cache
logger.debug("✅ Cache bound to app.extensions['cache']")

# === Inject BigQueryService ===
try:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cheetah-insurance-broker")
    bq_service = BigQueryService(project_id=project_id, location="asia-southeast1")
    app.extensions["bigquery_service"] = bq_service
    logger.info(f"✅ BigQueryService injected: {project_id}")
except Exception as e:
    logger.critical(f"❌ BigQueryService init failed: {e}")
    raise

# === Register Blueprints ===
try:
    set_app_instance(app)
    register_blueprints(app)
    logger.info("✅ Blueprints registered.")
except Exception as e:
    logger.error(f"❌ Blueprint registration failed: {e}")
    raise

# === Initialize DB Tables + Models ===
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

# === Health Check ===
@app.route("/api/health", methods=["GET"])
def health_check():
    return {"status": "ok"}, 200
