# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/__init__.py
import logging
import os
from flask import Flask
from dotenv import load_dotenv

# === Load .env ===
load_dotenv()

# === External Services & Extensions ===
from backend.services.bigquery_service import BigQueryService
from backend.extensions import cache

# === Core Utilities ===
from backend.routes.multi_step_search import set_app_instance
from backend.routes.line_webhook import line_webhook
from backend.routes.static_routes import setup_static_file_routes  # ✅ ใช้ function นี้แทน register ซ้ำ

def register_blueprints(app: Flask):
    if not isinstance(app, Flask):
        raise TypeError("The provided app object is not an instance of Flask.")

    logging.info("🔧 Registering blueprints...")

    try:
        # === Feature Blueprints ===
        from backend.routes.admin_routes import admin_bp
        from backend.routes.customer_info_routes import customer_info_bp
        from backend.routes.payment_routes import payment_bp
        from backend.routes.uploaded_documents_routes import uploaded_documents_bp
        from backend.routes.customer_policies_routes import customer_policies_bp
        from backend.routes.policy_routes import policy_bp
        from backend.routes.bigquery_routes import bigquery_bp
        from backend.routes.compare_routes import compare_bp
        from backend.routes.user_routes import user_bp
        from backend.routes.insurance_options_routes import insurance_options_bp
        from backend.routes.car_options_routes import car_options_bp
        from backend.routes.auth_routes import auth_bp
        from backend.routes.insurance_preparation_routes import insurance_preparation_bp
        from backend.routes.ocr_routes import ocr_bp
        from backend.routes.claim_routes import claim_bp
        from backend.routes.review_routes import review_bp
        from backend.routes.filter_packages import filter_packages_bp
        from backend.routes.multi_step_search import multi_step_search_bp
        from backend.routes.chatbot_routes import chatbot_bp
        from backend.routes.gallery_routes import gallery_api_bp
        from backend.routes.ollama_routes import ollama_bp
        from backend.routes.intent_router import intent_bp
        from backend.routes.ping_routes import ping_bp


    except ImportError as e:
        logging.critical(f"❌ ImportError while loading blueprints: {e}")
        raise

    def api(bp, path):
        return {"blueprint": bp, "url_prefix": f"/api{path}"}

    blueprints = [
        api(chatbot_bp, "/chatbot"),
        api(ollama_bp, "/ollama"),
        {"blueprint": intent_bp, "url_prefix": None},
        api(admin_bp, "/admins"),
        api(customer_info_bp, "/customer-info"),
        api(payment_bp, "/payments"),
        api(uploaded_documents_bp, "/documents"),
        api(customer_policies_bp, "/policies"),
        api(policy_bp, "/policy"),
        api(bigquery_bp, "/bigquery"),
        api(compare_bp, "/compare"),
        api(user_bp, "/user"),
        api(auth_bp, "/auth"),
        api(insurance_options_bp, "/insurance-options"),
        api(car_options_bp, "/car-options"),
        api(insurance_preparation_bp, "/insurance-preparation"),
        api(ocr_bp, "/ocr"),
        api(claim_bp, "/claims"),
        api(review_bp, "/reviews"),
        api(filter_packages_bp, "/filter-packages"),
        api(multi_step_search_bp, "/multi-step-search"),
        api(gallery_api_bp, "/gallery"),
        api(line_webhook, "/line-webhook"),
        api(ping_bp, "/ping"),
    ]

    registered = set()
    for bp in blueprints:
        b = bp["blueprint"]
        prefix = bp.get("url_prefix")
        if b.name in registered:
            logging.warning(f"⚠️ Duplicate blueprint name: {b.name} — Skipping")
            continue
        if prefix in (None, ""):
            app.register_blueprint(b)
            logging.info(f"✅ Registered '{b.name}' at internal url_prefix")
        else:
            app.register_blueprint(b, url_prefix=prefix)
            logging.info(f"✅ Registered '{b.name}' at '{prefix}'")
        registered.add(b.name)


def configure_app(app: Flask):
    set_app_instance(app)

    # Init Cache
    cache.init_app(app)
    app.extensions["cache"] = cache

    # Static File Serving
    setup_static_file_routes(app)  # ✅ สำคัญ

    # BigQuery Service
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cheetah-prod-analytics")
        bq_service = BigQueryService(project_id=project_id, location="asia-southeast1")
        app.extensions["bigquery_service"] = bq_service
        logging.info(f"✅ BigQueryService injected with project_id: {project_id}")
    except Exception as e:
        logging.critical(f"❌ Failed to initialize BigQueryService: {e}")
        raise

