# /Users/apichet/Downloads/cheetah-insurance-app/routes/insurance_options_routes.py
from flask import Blueprint, request, jsonify, current_app
import logging

# ✅ Initialize Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ✅ Initialize Blueprint
insurance_options_bp = Blueprint('insurance_options', __name__)


# ✅ ใช้ BigQuery Client จาก app.extensions
def get_bigquery_client():
    try:
        if "bigquery_service" in current_app.extensions:
            return current_app.extensions["bigquery_service"].client
        else:
            raise RuntimeError("BigQuery service is not registered.")
    except Exception as e:
        logger.error(f"❌ Failed to get BigQuery client: {str(e)}")
        raise


@insurance_options_bp.route('/insurance_coverage', methods=['GET'])
def get_insurance_coverage():
    """
    Endpoint สำหรับดึงข้อมูลความคุ้มครองของแพ็กเกจประกันภัย
    """
    try:
        package_id = request.args.get('package_code')

        if not package_id:
            return jsonify({"error": "package_code is required"}), 400

        client = get_bigquery_client()

        query = """
        SELECT 
            own_damage,
            own_theft_fire_damage AS theft_fire_damage,
            coverage_medical_expense AS medical_expense,
            liability_property,
            liability_per_person,
            liability_per_event,
            liability_deductible,
            coverage_driver_death,
            covearage_passenger_death AS coverage_passenger_death,
            coverage_bail_bond AS bail_bond,
            cmi_amount
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE package_code = @package_id
        """

        from google.cloud import bigquery  # Import inside function to avoid top-level dependency
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("package_id", "STRING", package_id)
            ]
        )

        query_job = client.query(query, job_config=job_config)
        result = query_job.result()
        coverage_data = next(result, None)

        if not coverage_data:
            return jsonify({"message": "Coverage data not found"}), 404

        return jsonify({
            "package_code": package_id,
            "coverage": {
                "own_damage": coverage_data.get("own_damage", 0),
                "theft_fire_damage": coverage_data.get("theft_fire_damage", 0),
                "medical_expense": coverage_data.get("medical_expense", 0),
                "liability_property": coverage_data.get("liability_property", 0),
                "liability_per_person": coverage_data.get("liability_per_person", 0),
                "liability_per_event": coverage_data.get("liability_per_event", 0),
                "liability_deductible": coverage_data.get("liability_deductible", 0),
                "coverage_driver_death": coverage_data.get("coverage_driver_death", 0),
                "coverage_passenger_death": coverage_data.get("coverage_passenger_death", 0),
                "bail_bond": coverage_data.get("bail_bond", 0),
                "cmi_amount": coverage_data.get("cmi_amount", 0)
            }
        }), 200

    except Exception as e:
        logger.exception(f"❌ Error fetching insurance coverage: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
