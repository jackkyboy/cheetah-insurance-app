# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/bigquery_routes.py
from flask import Blueprint, request, jsonify, current_app
from google.cloud import bigquery
from google.api_core.exceptions import BadRequest, NotFound
import os
import logging
import time
import math

# === Blueprint ===
bigquery_bp = Blueprint("bigquery", __name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# === Global BigQuery client ===
bigquery_client = None

# === Logo Mapping ===
COMPANY_NAME_MAPPING = {
    "chubb": "CHUBB-logo.svg",
    "ergo": "ERGO-logo.svg",
    "mti": "MTI-logo.svg",
    "tokio marine": "TOKIO-MARINE-logo.svg",
    "viriyah": "VIRIYAH-logo.svg"
}


def get_bigquery_client():
    """
    ✅ ใช้ Singleton ป้องกัน client ซ้ำซ้อน
    ✅ โหลด BigQuery client ด้วย project ที่กำหนดเอง
    ✅ ตรวจสอบว่า GOOGLE_APPLICATION_CREDENTIALS ถูกตั้งไว้
    """
    global bigquery_client

    if bigquery_client:
        return bigquery_client

    try:
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            raise EnvironmentError("🌐 Environment variable 'GOOGLE_APPLICATION_CREDENTIALS' not set.")
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"🔐 Credentials file not found at path: {credentials_path}")

        logger.debug(f"🔄 Initializing BigQuery client using: {credentials_path}")

        bigquery_client = bigquery.Client.from_service_account_json(
            credentials_path,
            project="cheetah-insurance-broker"  # ✅ บังคับใช้ project ตรงนี้
        )

        logger.info("✅ BigQuery client initialized successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to initialize BigQuery client: {e}", exc_info=True)
        raise RuntimeError(f"Failed to initialize BigQuery client: {e}")

    return bigquery_client



def map_company_name_to_thai(company_name):
    return COMPANY_NAME_MAPPING.get(company_name.lower(), "Unknown Company")

def map_insurance_type_group(input_type: str):
    key = input_type.strip().lower() if input_type else "0"
    key = key.replace(" ", "").replace("ชั้น", "")

    if key in ["1", "type1"]:
        return ["1"]
    elif key in ["2", "type2"]:
        return ["2"]  # ✅ ไม่รวม 2+ หรือ 2P
    elif key in ["2+", "2plus", "2p", "type2+"]:
        return ["2+", "2p"]
    elif key in ["3+", "3plus", "3p", "type3+"]:
        return ["3+", "3p"]
    elif key in ["3", "type3"]:
        return ["3"]
    else:
        return ["0"]



def build_query_parameters(data, insurance_type_group, limit, offset):
    submodel = data.get("car_submodel", "").strip().lower()
    submodel = None if not submodel else f"%{submodel}%"

    return [
        bigquery.ScalarQueryParameter("car_brand", "STRING", data["car_brand"]),
        bigquery.ScalarQueryParameter("car_model", "STRING", data["car_model"]),
        bigquery.ScalarQueryParameter("car_model_year", "STRING", data["car_model_year"]),
        bigquery.ArrayQueryParameter("insurance_types", "STRING", insurance_type_group),
        bigquery.ScalarQueryParameter("car_submodel", "STRING", submodel),
        bigquery.ScalarQueryParameter("limit", "INT64", limit),
        bigquery.ScalarQueryParameter("offset", "INT64", offset)
    ]


def format_result_rows(rows):
    grouped = {}
    for row in rows:
        repair_type = row.get("repair_type", "N/A")
        grouped.setdefault(repair_type, []).append({
            "package_code": row.get("package_code"),
            "company_name": row.get("company_name"),
            "company_name_th": map_company_name_to_thai(row.get("company_name")),
            "car_brand": row.get("car_brand"),
            "car_model": row.get("car_model"),
            "car_submodel": row.get("car_submodel", "N/A"),
            "car_model_year": row.get("car_model_year"),
            "insurance_type": row.get("insurance_type"),
            "repair_type": repair_type,
            "premium": row.get("premium", 0),
            "coverage": {
                "own_damage": row.get("own_damage"),
                "theft_fire_damage": row.get("own_theft_fire_damage"),
                "medical_expense": row.get("coverage_medical_expense"),
                "bail_bond": row.get("coverage_bail_bond"),
                "cmi_amount": row.get("cmi_amount"),
                "liability": {
                    "per_person": row.get("liability_per_person"),
                    "per_event": row.get("liability_per_event"),
                    "property": row.get("liability_property"),
                    "deductible": row.get("liability_deductible"),
                }
            }
        })
    return grouped
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/bigquery_routes.py
@bigquery_bp.route('/query', methods=['POST'])
def compare_insurance():
    try:
        start_time = time.time()
        data = request.get_json()
        logger.info(f"🔍 Request received: {data}")

        for field in ["car_brand", "car_model", "car_model_year", "insurance_type"]:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        car_brand = data["car_brand"].strip().lower()
        car_model = data["car_model"].strip().lower()
        car_model_year = str(data["car_model_year"]).strip()
        car_submodel = data.get("car_submodel", "").strip().lower()
        insurance_type_group = map_insurance_type_group(data["insurance_type"])

        if not car_model_year.isdigit():
            return jsonify({"error": "car_model_year must be numeric"}), 400

        page = int(data.get("page", 1))
        limit = int(data.get("limit", 10))
        offset = (page - 1) * limit

        QUERY = """
        SELECT
            package_code, Insurance_company AS company_name,
            LOWER(car_brand) AS car_brand, LOWER(car_model) AS car_model,
            LOWER(car_submodel) AS car_submodel, car_model_year,
            insurance_type, repair_type, premium, cmi_amount,
            liability_per_person, liability_per_event, liability_property,
            liability_deductible, own_damage, own_theft_fire_damage,
            coverage_driver_death, covearage_passenger_death,
            coverage_medical_expense, coverage_bail_bond,
            COUNT(*) OVER() AS total_rows
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE LOWER(car_brand) = @car_brand
          AND LOWER(car_model) = @car_model
          AND car_model_year = @car_model_year
          AND insurance_type IN UNNEST(@insurance_types)
          AND (
              @car_submodel IS NULL
              OR @car_submodel = ''
              OR LOWER(car_submodel) LIKE CONCAT('%', LOWER(@car_submodel), '%')
          )
        ORDER BY repair_type
        LIMIT @limit OFFSET @offset
        """

        query_params = build_query_parameters(
            {
                "car_brand": car_brand,
                "car_model": car_model,
                "car_model_year": car_model_year,
                "car_submodel": car_submodel
            },
            insurance_type_group,
            limit,
            offset
        )

        client = get_bigquery_client()
        query_job = client.query(QUERY, job_config=bigquery.QueryJobConfig(query_parameters=query_params))
        results = [dict(row) for row in query_job.result()]

        if not results:
            logger.info("ℹ️ No data found. Running fallback query...")

            fallback_data = {
                "available_years": [],
                "available_insurance_types": [],
                "similar_companies": []
            }

            # === Fallback: หาปีที่มีข้อมูล ===
            year_query = """
                SELECT DISTINCT car_model_year
                FROM `cheetah-insurance-broker.insurance.insurance_data_center`
                WHERE LOWER(car_brand) = @car_brand
                AND LOWER(car_model) = @car_model
                ORDER BY car_model_year DESC
                LIMIT 5
            """
            year_job = client.query(year_query, job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                    bigquery.ScalarQueryParameter("car_model", "STRING", car_model)
                ]
            ))
            fallback_data["available_years"] = [row["car_model_year"] for row in year_job.result()]

            # === Fallback: หาประเภทประกัน ===
            type_query = """
                SELECT DISTINCT insurance_type
                FROM `cheetah-insurance-broker.insurance.insurance_data_center`
                WHERE LOWER(car_brand) = @car_brand
                AND LOWER(car_model) = @car_model
                AND car_model_year IN UNNEST(@years)
            """
            type_job = client.query(type_query, job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                    bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
                    bigquery.ArrayQueryParameter("years", "STRING", fallback_data["available_years"])
                ]
            ))
            fallback_data["available_insurance_types"] = [row["insurance_type"] for row in type_job.result()]

            # === Fallback: หาบริษัทที่เกี่ยวข้อง ===
            company_query = """
                SELECT DISTINCT Insurance_company
                FROM `cheetah-insurance-broker.insurance.insurance_data_center`
                WHERE LOWER(car_brand) = @car_brand
                AND LOWER(car_model) = @car_model
                LIMIT 5
            """
            company_job = client.query(company_query, job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                    bigquery.ScalarQueryParameter("car_model", "STRING", car_model)
                ]
            ))
            fallback_data["similar_companies"] = [row["Insurance_company"] for row in company_job.result()]

            return jsonify({
                "message": "No data found",
                "results": [],
                "fallbacks": fallback_data
            }), 200

        # ✅ ถ้ามีผลลัพธ์จริง → ต้อง return
        return jsonify({
            "message": "Success",
            "results": results,
            "total": results[0]["total_rows"] if results else 0
        }), 200

    except BadRequest as e:
        logger.error(f"❌ BigQuery BadRequest Error: {e}")
        return jsonify({"error": "Bad request to BigQuery", "details": str(e)}), 400
    except NotFound as e:
        logger.error(f"❌ BigQuery NotFound Error: {e}")
        return jsonify({"error": "Requested data or table not found", "details": str(e)}), 404
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500



@bigquery_bp.route("/car-submodels", methods=["GET"])
def car_submodels_route():
    try:
        # ✅ ดึงค่าจาก query params
        car_brand = request.args.get("car_brand")
        car_model = request.args.get("car_model")
        car_model_year = request.args.get("car_model_year")
        limit = int(request.args.get("limit", 10))

        if not all([car_brand, car_model, car_model_year]):
            return jsonify({"error": "Missing required query parameters"}), 400

        submodels = fetch_car_submodels(car_brand, car_model, car_model_year, limit)
        return jsonify({"submodels": submodels})

    except Exception as e:
        logger.error(f"❌ Failed to fetch car submodels: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


def fetch_car_submodels(car_brand, car_model, car_model_year, limit=10):
    """
    🔍 ดึงรายการ car_submodel จาก BigQuery ตามยี่ห้อ/รุ่น/ปี
    """
    try:
        client = get_bigquery_client()
        query = """
        SELECT DISTINCT car_submodel
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand
          AND car_model = @car_model
          AND car_model_year = @car_model_year
          AND car_submodel IS NOT NULL
        LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
                bigquery.ScalarQueryParameter("car_model_year", "STRING", car_model_year),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        return [row["car_submodel"] for row in results]

    except Exception as e:
        logger.error(f"❌ Error fetching submodels from BigQuery: {e}", exc_info=True)
        return []
