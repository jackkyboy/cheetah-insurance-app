from flask import Blueprint, request, jsonify
from backend.services.vmi_service import VMIService

vmi_routes = Blueprint("vmi_routes", __name__)

@vmi_routes.route("/vmi/quotation", methods=["POST"])
def get_vmi_quotation():
    payload = request.get_json()
    result = VMIService.get_quotation(payload)
    return jsonify(result)
