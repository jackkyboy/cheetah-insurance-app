# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/static_routes.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/static_routes.py

import os
import logging
from flask import Blueprint, jsonify, current_app, send_from_directory

# === Logger ===
logger = logging.getLogger(__name__)

# ✅ ไม่ใช้ชื่อ 'static' ที่ชน system route
static_files_bp = Blueprint("static_files_bp", __name__)

# === Utility ===
def get_safe_file_path(directory, filename):
    return os.path.join(directory, os.path.basename(filename))


# === Serve Uploaded Logos ===
@static_files_bp.route("/logos/<filename>", methods=["GET"])
def serve_logo(filename):
    logos_dir = os.path.join(current_app.root_path, "uploads", "logos")
    fallback_logo = "default-logo.svg"
    safe_filename = os.path.basename(filename)
    full_path = get_safe_file_path(logos_dir, safe_filename)

    logger.info(f"🔍 Request logo: {safe_filename}")
    if os.path.isfile(full_path):
        return send_from_directory(logos_dir, safe_filename)
    else:
        logger.warning(f"❌ Logo not found: {full_path}. Using fallback.")
        return send_from_directory(logos_dir, fallback_logo), 404


# === Check Logo Existence ===
@static_files_bp.route("/logos/check/<filename>", methods=["GET"])
def check_logo(filename):
    logos_dir = os.path.join(current_app.root_path, "uploads", "logos")
    safe_filename = os.path.basename(filename)
    file_path = get_safe_file_path(logos_dir, safe_filename)

    exists = os.path.isfile(file_path)
    logger.info(f"{'✅ Found' if exists else '❌ Not found'}: {safe_filename}")
    return jsonify({"exists": exists}), (200 if exists else 404)


# === Serve Profile Picture ===
@static_files_bp.route("/uploads/profile_pictures/<filename>", methods=["GET"])
def serve_profile_picture(filename):
    picture_dir = os.path.join(current_app.root_path, "uploads", "profile_pictures")
    safe_filename = os.path.basename(filename)
    full_path = get_safe_file_path(picture_dir, safe_filename)

    logger.debug(f"📁 picture_dir = {picture_dir}")
    logger.debug(f"📄 full_path = {full_path}")

    if os.path.isfile(full_path):
        logger.info(f"✅ Serving profile picture: {safe_filename}")
        return send_from_directory(picture_dir, safe_filename)
    else:
        logger.warning(f"❌ Profile picture not found: {safe_filename}")
        return jsonify({"error": "Profile picture not found"}), 404



# === Serve Static Images from /static/images ===
@static_files_bp.route("/static/images/<path:filename>", methods=["GET"])
def serve_static_image(filename):
    image_dir = os.path.join(current_app.root_path, "static/images")
    safe_filename = os.path.basename(filename)
    full_path = get_safe_file_path(image_dir, safe_filename)

    logger.info(f"🖼️ Request static image: {safe_filename}")
    if os.path.isfile(full_path):
        return send_from_directory(image_dir, safe_filename)
    else:
        logger.warning(f"❌ Static image not found: {full_path}")
        return jsonify({"error": "Image not found"}), 404


# === Blueprint Registration ===
def setup_static_file_routes(app):
    if "static_files_bp" not in app.blueprints:
        app.register_blueprint(static_files_bp, url_prefix="/api")
        logger.info("✅ static_files_bp registered at /api")
    else:
        logger.warning("⚠️ static_files_bp already registered. Skipping.")


# === SPA Fallback ===
@static_files_bp.route("/", defaults={"path": ""})
@static_files_bp.route("/<path:path>")
def serve_frontend(path):
    # ⛔️ ป้องกันไม่ให้ fallback ไปกิน route /api/*
    if path.startswith("api"):
        logger.debug(f"🚫 Ignoring /{path} — it's an API route.")
        return jsonify({"error": "API not found"}), 404

    static_root = os.path.join(current_app.root_path, "static")
    real_file = os.path.join(static_root, path)

    if os.path.isfile(real_file):
        try:
            return send_from_directory(os.path.dirname(real_file), os.path.basename(real_file))
        except Exception as e:
            logger.error(f"❌ Error serving static file: {e}")
            return jsonify({"error": "Static file error"}), 500

    try:
        logger.debug(f"🌐 Fallback route hit: /{path}")
        return send_from_directory(current_app.static_folder, "index.html")
    except Exception as e:
        logger.exception("❌ Failed to serve frontend")
        return jsonify({"error": "Frontend Error"}), 500
