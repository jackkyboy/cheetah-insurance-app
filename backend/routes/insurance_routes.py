from flask import Blueprint, request, jsonify
from backend.services.vmi_service import VMIService

insurance_bp = Blueprint("insurance", __name__)

@insurance_bp.route("/insurance-companies", methods=["POST"])
def create_insurance_company():
    """
    API สำหรับเพิ่มบริษัทประกันภัยใหม่
    """
    try:
        data = request.json
        company_name = data.get("company_name")
        api_endpoint = data.get("api_endpoint")
        if not company_name or not api_endpoint:
            return jsonify({"error": "company_name and api_endpoint are required"}), 400

        company = InsuranceCompanyService.create_company(
            company_name=company_name,
            api_endpoint=api_endpoint,
            api_token=data.get("api_token"),
            token_expiration=data.get("token_expiration")
        )
        return jsonify({"message": "Insurance company created successfully", "company_id": company.company_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@insurance_bp.route("/insurance-companies/<int:company_id>", methods=["GET"])
def get_insurance_company(company_id):
    """
    API สำหรับดึงข้อมูลบริษัทประกันภัยจาก company_id
    """
    try:
        company = InsuranceCompanyService.get_company_by_id(company_id)
        return jsonify({
            "company_id": company.company_id,
            "company_name": company.company_name,
            "api_endpoint": company.api_endpoint,
            "api_token": company.api_token,
            "token_expiration": company.token_expiration,
            "last_token_refresh": company.last_token_refresh
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@insurance_bp.route("/insurance-companies", methods=["GET"])
def get_all_insurance_companies():
    """
    API สำหรับดึงข้อมูลบริษัทประกันภัยทั้งหมด
    """
    try:
        companies = InsuranceCompanyService.get_all_companies()
        return jsonify([
            {
                "company_id": company.company_id,
                "company_name": company.company_name,
                "api_endpoint": company.api_endpoint
            }
            for company in companies
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@insurance_bp.route("/insurance-companies/<int:company_id>/token", methods=["GET"])
def get_api_token(company_id):
    """
    API สำหรับดึง Token ของบริษัทประกันภัย
    """
    try:
        token = InsuranceCompanyService.get_valid_api_token(company_id)
        return jsonify({"api_token": token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
