
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/ping_routes.py
# /backend/routes/ping_routes.py
from flask import Blueprint, jsonify

ping_bp = Blueprint("ping_bp", __name__)

@ping_bp.route("/", methods=["GET"])
def ping():
    return jsonify({"message": "pong"}), 200
