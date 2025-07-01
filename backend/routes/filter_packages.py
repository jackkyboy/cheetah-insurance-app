# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/filter_packages.py
import requests
from flask import Blueprint, request, jsonify
from backend.services.bigquery_service import BigQueryService
from flask_jwt_extended import jwt_required
from flask_cors import CORS
import logging
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest

# ✅ Initialize Blueprint
filter_packages_bp = Blueprint("filter_packages", __name__, url_prefix="/api/filter-packages")
filter_packages_bp.strict_slashes = False

# ✅ Enable CORS
CORS(filter_packages_bp)

# ✅ Initialize BigQuery Service
bigquery_service = BigQueryService(project_id="cheetah-insurance-broker", location="asia-southeast1")

# ✅ เพิ่ม Debugging Logging
logging.basicConfig(level=logging.DEBUG)

@filter_packages_bp.route("", methods=["POST"])
@jwt_required()
def filter_packages():
    """
    ✅ Apply filters AFTER fetching packages from Multi-Step Search
    ✅ ใช้ API `/fetch_packages` ก่อน แล้ว Filter ตาม
    """
    try:
        data = request.get_json()
        if not data:
            logging.error("❌ Invalid request format. JSON payload required.")
            return jsonify({"error": "Invalid request format. JSON payload required"}), 400

        logging.debug(f"📥 Received filters: {data}")

        # ✅ เรียก API `/fetch_packages` ก่อน
        fetch_url = "http://127.0.0.1:5000/api/multi-step-search/fetch_packages"
        try:
            response = requests.post(fetch_url, json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"❌ Failed to fetch packages: {str(e)}")
            return jsonify({"error": "Failed to fetch packages", "details": str(e)}), 500

        # ✅ ตรวจสอบโครงสร้างข้อมูลที่ได้จาก API
        try:
            packages_data = response.json()
            packages = packages_data.get("packages", [])
            if not isinstance(packages, list):
                raise ValueError("❌ Invalid response format: 'packages' should be a list")
        except Exception as e:
            logging.error(f"❌ Error parsing API response: {str(e)}")
            return jsonify({"error": "Invalid API response format"}), 500

        logging.debug(f"🔍 Retrieved {len(packages)} packages from /fetch_packages")

        if not packages:
            logging.warning("⚠️ No packages found after fetching.")
            return jsonify({"available_filters": packages_data, "packages": []}), 200

        # ✅ Apply Filters ใน Memory
        selected_company = data.get("selectedCompany")
        premium_max = data.get("premiumMax")
        repair_type = data.get("repairType")

        if selected_company:
            logging.debug(f"🔍 Filtering by selected_company: {selected_company}")
            packages = [pkg for pkg in packages if pkg.get("company") == selected_company]

        if premium_max:
            try:
                premium_max = float(premium_max)
                logging.debug(f"🔍 Filtering by premium_max: {premium_max}")
                packages = [pkg for pkg in packages if float(pkg.get("premium", 0)) <= premium_max]
            except ValueError:
                logging.warning(f"⚠️ premiumMax '{premium_max}' is not a valid float.")

        if repair_type:
            logging.debug(f"🔍 Filtering by repair_type: {repair_type}")
            packages = [pkg for pkg in packages if pkg.get("repair_type", "").lower() == repair_type.lower()]

        # ✅ อัพเดตตัวกรองที่เหลือ
        available_companies = list(set(pkg.get("company") for pkg in packages if "company" in pkg))
        available_repair_types = list(set(pkg.get("repair_type") for pkg in packages if "repair_type" in pkg))
        price_range = {
            "min": min(float(pkg.get("premium", 0)) for pkg in packages) if packages else 0,
            "max": max(float(pkg.get("premium", 0)) for pkg in packages) if packages else 0,
        }

        logging.info(f"✅ Returning {len(packages)} filtered packages.")

        return jsonify({
            "available_filters": {
                "available_companies": available_companies,
                "available_repair_types": available_repair_types,
                "price_range": price_range
            },
            "packages": packages
        }), 200

    except Exception as e:
        logging.error(f"❌ Unexpected error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while filtering packages.", "details": str(e)}), 500


@filter_packages_bp.route('/options', methods=['GET'])
def filter_options():
    """
    Retrieve unique filter options for companies, submodels, and repair types.
    """
    try:
        query = """
        SELECT DISTINCT
            insurance_company AS company_name,
            car_submodel,
            repair_type
        FROM
            `cheetah-insurance-broker.insurance.insurance_data_center`
        """
        client = bigquery_service.client
        query_job = client.query(query)
        results = query_job.result()

        options = [dict(row) for row in results]

        logging.info(f"✅ Retrieved {len(options)} filter options.")
        return jsonify(options), 200

    except Exception as e:
        logging.error(f"❌ Failed to retrieve filter options: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while retrieving options."}), 500
