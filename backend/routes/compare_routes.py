# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/compare_routes.py
from flask import Blueprint, request, jsonify
from backend.services.bigquery_service import BigQueryService
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from google.cloud import bigquery

compare_bp = Blueprint('compare', __name__)

# BigQuery Service setup
bigquery_service = BigQueryService(
    project_id="cheetah-insurance-broker",
    location="asia-southeast1"
)

@compare_bp.route('/compare', methods=['GET'])
@jwt_required()
def compare_insurance():
    """
    API for comparing insurance packages using user_id from JWT Token
    """
    try:
        user_id = get_jwt_identity()
        logging.info(f"User {user_id} is accessing compare_insurance.")

        # Get query parameters
        car_brand = request.args.get('car_brand', "").strip()
        car_model_year = request.args.get('car_model_year', "").strip()
        car_model = request.args.get('car_model', "").strip()
        insurance_type = request.args.get('insurance_type', "").strip()
        car_submodel = request.args.get('car_submodel', "").strip() or None  # Convert empty string to None
        has_camera = request.args.get('has_camera', 'false').lower() == 'true'

        # Validate required parameters
        if not all([car_brand, car_model_year, car_model, insurance_type]):
            logging.error("Missing required parameters.")
            return jsonify({"error": "Missing required parameters"}), 400

        # BigQuery SQL Query
        QUERY = """
        SELECT
            COALESCE(Insurance_company, "ไม่ระบุ") AS company_name,
            COALESCE(car_brand, "ไม่ระบุ") AS car_brand,
            COALESCE(car_model, "ไม่ระบุ") AS car_model,
            COALESCE(car_submodel, "ไม่ระบุ") AS car_submodel,
            COALESCE(car_model_year, "ไม่ระบุ") AS car_model_year,
            COALESCE(insurance_type, "ไม่ระบุ") AS insurance_type,
            COALESCE(premium, 0) AS premium,
            COALESCE(repair_type, "ไม่ระบุ") AS repair_type,
            COALESCE(cmi_amount, 0) AS cmi_amount,
            COALESCE(liability_per_person, 0) AS liability_per_person,
            COALESCE(liability_per_event, 0) AS liability_per_event,
            COALESCE(liability_property, 0) AS liability_property,
            COALESCE(liability_deductible, 0) AS liability_deductible,
            COALESCE(own_damage, 0) AS own_damage,
            COALESCE(own_theft_fire_damage, 0) AS own_theft_fire_damage,
            COALESCE(coverage_driver_death, 0) AS coverage_driver_death,
            COALESCE(coverage_passenger_death, 0) AS coverage_passenger_death,
            COALESCE(coverage_medical_expense, 0) AS coverage_medical_expense,
            COALESCE(coverage_bail_bond, 0) AS coverage_bail_bond
        FROM
            `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE
            car_brand = @car_brand
            AND car_model_year = @car_model_year
            AND car_model = @car_model
            AND insurance_type = @insurance_type
            AND (@car_submodel IS NULL OR car_submodel = @car_submodel)
        """
        parameters = [
            bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
            bigquery.ScalarQueryParameter("car_model_year", "STRING", car_model_year),
            bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
            bigquery.ScalarQueryParameter("insurance_type", "STRING", insurance_type),
            bigquery.ScalarQueryParameter("car_submodel", "STRING", car_submodel),
        ]

        # Execute BigQuery
        logging.info("Executing BigQuery")
        result, status_code = bigquery_service.execute_query(QUERY, parameters)

        # Adjust premium if has_camera is true
        if status_code == 200 and result:
            for item in result:
                if has_camera:
                    item['premium'] = round(float(item['premium']) * 0.95, 2)  # 5% discount

        # Format the response
        formatted_result = [
            {
                "company_name": item.get("company_name", "ไม่ระบุ"),
                "car_brand": item.get("car_brand", "ไม่ระบุ"),
                "car_model": item.get("car_model", "ไม่ระบุ"),
                "car_submodel": item.get("car_submodel", "ไม่ระบุ"),
                "car_model_year": item.get("car_model_year", "ไม่ระบุ"),
                "insurance_type": item.get("insurance_type", "ไม่ระบุ"),
                "repair_type": item.get("repair_type", "ไม่ระบุ"),
                "premium": item.get("premium", 0),
                "coverage": {
                    "cmi_amount": item.get("cmi_amount", 0),
                    "liability_per_person": item.get("liability_per_person", 0),
                    "liability_per_event": item.get("liability_per_event", 0),
                    "liability_property": item.get("liability_property", 0),
                    "liability_deductible": item.get("liability_deductible", 0),
                    "own_damage": item.get("own_damage", 0),
                    "own_theft_fire_damage": item.get("own_theft_fire_damage", 0),
                    "driver_death": item.get("coverage_driver_death", 0),
                    "passenger_death": item.get("coverage_passenger_death", 0),
                    "medical_expense": item.get("coverage_medical_expense", 0),
                    "bail_bond": item.get("coverage_bail_bond", 0),
                },
            }
            for item in result
        ]

        logging.info(f"User {user_id} retrieved insurance comparison data.")
        return jsonify(formatted_result), status_code

    except bigquery.exceptions.BadRequest as e:
        logging.error(f"BigQuery BadRequest Error: {e}")
        return jsonify({"error": "Bad request to BigQuery", "details": str(e)}), 400
    except bigquery.exceptions.NotFound as e:
        logging.error(f"BigQuery NotFound Error: {e}")
        return jsonify({"error": "Requested data or table not found", "details": str(e)}), 404
    except Exception as e:
        logging.error(f"Unexpected Error: {e}")
        return jsonify({"error": str(e)}), 500



@compare_bp.route('/insurance-packages', methods=['GET'])
def get_insurance_packages():
    """
    API สำหรับดึงข้อมูลแพ็คเกจประกันภัย
    """
    try:
        car_brand = request.args.get('car_brand', "").strip().lower()
        car_model = request.args.get('car_model', "").strip().lower()
        car_model_year = request.args.get('car_model_year', "").strip()
        insurance_type = request.args.get('insurance_type', "").strip()
        repair_type = request.args.get('repair_type', "").strip()

        # Validate parameters
        if not all([car_brand, car_model, car_model_year, insurance_type]):
            return jsonify({"error": "Missing required parameters"}), 400

        # BigQuery Query
        QUERY = """
        SELECT *
        FROM `cheetah-insurance-broker.insurance.insurance_data_center_bkup`
        WHERE LOWER(car_brand) = @car_brand
        AND LOWER(car_model) = @car_model
        AND car_model_year = @car_model_year
        AND insurance_type = @insurance_type
        AND repair_type = @repair_type
        """
        parameters = [
            bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
            bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
            bigquery.ScalarQueryParameter("car_model_year", "STRING", car_model_year),
            bigquery.ScalarQueryParameter("insurance_type", "STRING", insurance_type),
            bigquery.ScalarQueryParameter("repair_type", "STRING", repair_type),
        ]

        # Query BigQuery
        client = get_bigquery_client()
        query_job = client.query(
            QUERY, job_config=bigquery.QueryJobConfig(query_parameters=parameters)
        )
        results = query_job.result()
        packages = [dict(row) for row in results]

        if not packages:
            return jsonify({"message": "No packages found"}), 404

        return jsonify({"results": packages}), 200
    except Exception as e:
        logging.error(f"Error fetching insurance packages: {e}")
        return jsonify({"error": str(e)}), 500
