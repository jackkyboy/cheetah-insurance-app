from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug-jwt", methods=["GET"])
@jwt_required()
def debug_jwt():
    jwt_payload = get_jwt()
    return jsonify(jwt_payload)
