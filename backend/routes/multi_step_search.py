## /backend/routes/multi_step_search.py

from flask import Blueprint, request, jsonify
import logging
import traceback
from google.cloud import bigquery
from decimal import Decimal
from backend.extensions import cache  # ✅ ใช้ cache ที่ bind แล้ว
from functools import wraps

multi_step_search_bp = Blueprint("multi_step_search", __name__)

# === Patch: manual app injection ===
app_instance = None
def set_app_instance(app):
    global app_instance
    app_instance = app

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# ✅ ใช้ BigQuery client จาก app_instance
def get_bigquery_client():
    if not app_instance:
        raise RuntimeError("❌ app_instance not initialized.")
    bq_service = app_instance.extensions.get("bigquery_service")
    if bq_service and hasattr(bq_service, "client"):
        logger.debug("✅ BigQuery client retrieved from app_instance.extensions")
        return bq_service.client
    else:
        raise RuntimeError("❌ BigQuery service not found in app_instance.extensions.")

# ✅ Error handler
def handle_error(message, exception):
    logging.error(f"❌ {message}: {str(exception)}", exc_info=True)
    response = {"error": message}
    if app_instance and app_instance.config.get("DEBUG", False):
        response["details"] = str(exception)
    return jsonify(response), 500

# ✅ Custom decorator: ใช้ cache จาก app.extensions["cache"]["default"]
def use_default_cache(timeout=60, key_prefix=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        # Inject default cache instance manually
        cache_obj = app_instance.extensions.get("cache", {}).get("default")
        if cache_obj:
            return cache_obj.cached(timeout=timeout, key_prefix=key_prefix)(f)
        else:
            logger.warning("⚠️ Cache instance not found, fallback to uncached version.")
            return f
    return decorator


# ✅ ดึงยี่ห้อรถ
@multi_step_search_bp.route('/get_brand', methods=['GET'])
def get_brand():
    try:
        client = get_bigquery_client()
        QUERY = """
        SELECT DISTINCT car_brand 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        ORDER BY car_brand
        """
        query_job = client.query(QUERY)
        results = [row["car_brand"] for row in query_job.result() if row.get("car_brand")]
        logger.info(f"✅ Fetched {len(results)} car brands.")
        return jsonify(results), 200
    except Exception as e:
        return handle_error("Failed to fetch car brands", e)

# ✅ ดึงรุ่นจากยี่ห้อ
@multi_step_search_bp.route('/get_model', methods=['GET'])
def get_model():
    car_brand = request.args.get('car_brand')
    if not car_brand:
        return jsonify({"error": "Missing car_brand parameter"}), 400

    try:
        client = get_bigquery_client()
        QUERY = """
        SELECT DISTINCT car_model 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand
        ORDER BY car_model
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand)]
        )
        query_job = client.query(QUERY, job_config=job_config)
        results = [row["car_model"] for row in query_job.result()]
        logger.info(f"✅ Fetched {len(results)} models for brand '{car_brand}'.")
        return jsonify(results), 200
    except Exception as e:
        return handle_error("Failed to fetch car models", e)

# ✅ ดึงซับโมเดล
@multi_step_search_bp.route('/get_submodel', methods=['GET'])
def get_submodel():
    car_brand = request.args.get('car_brand')
    car_model = request.args.get('car_model')
    if not car_brand or not car_model:
        return jsonify({"error": "Missing required parameters: car_brand, car_model"}), 400

    try:
        client = get_bigquery_client()
        QUERY = """
        SELECT DISTINCT car_submodel 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand AND car_model = @car_model
        ORDER BY car_submodel
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                bigquery.ScalarQueryParameter("car_model", "STRING", car_model)
            ]
        )
        query_job = client.query(QUERY, job_config=job_config)
        results = [row["car_submodel"] for row in query_job.result() if row["car_submodel"]]
        logger.info(f"✅ Fetched {len(results)} submodels for '{car_brand}' - '{car_model}'.")
        return jsonify(results), 200
    except Exception as e:
        return handle_error("Failed to fetch car submodels", e)

# ✅ ดึงปีรุ่น
@multi_step_search_bp.route('/get_years', methods=['GET'])
def get_years():
    car_brand = request.args.get('car_brand')
    car_model = request.args.get('car_model')

    if not car_brand or not car_model:
        return jsonify({"error": "Missing required parameters: car_brand, car_model"}), 400

    try:
        client = get_bigquery_client()
        QUERY = """
        SELECT DISTINCT car_model_year 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand AND car_model = @car_model
        ORDER BY car_model_year DESC
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
            ]
        )
        query_job = client.query(QUERY, job_config=job_config)
        results = [row["car_model_year"] for row in query_job.result()]
        logger.info(f"✅ Fetched {len(results)} car model years for '{car_brand}' '{car_model}'.")
        return jsonify({"car_model_years": results}), 200
    except Exception as e:
        return handle_error("Failed to fetch car model years", e)
    


    
# ✅ Route: Fetch Repair Types
@multi_step_search_bp.route('/get_repair_types', methods=['GET'])
@cache.cached(timeout=60, key_prefix="repair_types")  # ✅ ใช้ key_prefix เฉย ๆ
def get_repair_types():
    try:
        client = get_bigquery_client()

        QUERY = """
        SELECT DISTINCT repair_type 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE repair_type IS NOT NULL
        """
        query_job = client.query(QUERY)
        raw_results = [row["repair_type"] for row in query_job.result()]

        allowed_types = {
            "ซ่อมอู่": "ซ่อมอู่",
            "ซ่อมห้าง": "ซ่อมห้าง",
            "ซ่อมอู่ห้าง": "ซ่อมห้าง",
            "ซ่อมอู่ประกัน": "ซ่อมอู่"
        }

        # ✅ แปลงเป็นชุดผลลัพธ์ที่ normalize แล้ว
        filtered_results = sorted(set(
            allowed_types.get(rt.strip(), None)
            for rt in raw_results if rt and rt.strip() in allowed_types
        ))

        # ✅ ลบค่า None ออก
        filtered_results = [rt for rt in filtered_results if rt]

        logger.info(f"✅ Repair types: {filtered_results}")
        return jsonify({"repair_types": filtered_results}), 200

    except Exception as e:
        logger.exception("❌ Failed to fetch repair types")
        return jsonify({"repair_types": []}), 500



# ✅ Route: Fetch Insurance Types (Normalized + Cached)
@multi_step_search_bp.route('/get_insurance_types', methods=['GET'])
@cache.cached(timeout=60, key_prefix="insurance_types")
def get_insurance_types():
    try:
        client = get_bigquery_client()

        QUERY = """
        SELECT DISTINCT insurance_type 
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE insurance_type IS NOT NULL
        """
        query_job = client.query(QUERY)
        raw_results = [row["insurance_type"] for row in query_job.result()]

        insurance_map = {
            "1": "1",
            "2": "2",
            "2P": "2+",
            "3": "3",
            "3P": "3+"
        }

        filtered_results = sorted(set(
            insurance_map[it] for it in raw_results if it in insurance_map
        ))

        logger.info(f"✅ Insurance types: {filtered_results}")
        return jsonify({"insurance_types": filtered_results}), 200

    except Exception as e:
        return handle_error("Failed to fetch insurance types", e)




# Helper Function: Parse Pagination Parameters
def parse_pagination(data):
    try:
        page = int(data.get("page", 1))
        limit = int(data.get("limit", 10))
        if page <= 0 or limit <= 0:
            raise ValueError("Page and limit must be positive integers.")
        offset = (page - 1) * limit
        return page, limit, offset
    except ValueError as e:
        raise ValueError(f"Invalid pagination parameters: {str(e)}")

# Route: Fetch Insurance Packages
@multi_step_search_bp.route("/fetch_packages", methods=["POST"])
def fetch_packages():
    """
    Fetch insurance packages with pagination.
    """
    data = request.get_json()

    # Validate required parameters
    car_brand = data.get("car_brand")
    car_model = data.get("car_model")
    car_model_year = data.get("car_model_year")
    repair_type = data.get("repair_type", "ซ่อมอู่")  # Default to "ซ่อมอู่"

    if not all([car_brand, car_model, car_model_year]):
        logging.warning("❌ Missing required parameters: car_brand, car_model, car_model_year.")
        return jsonify({"error": "Missing required parameters: car_brand, car_model, car_model_year"}), 400

    try:
        # ✅ เพิ่มการกำหนดค่า client
        client = get_bigquery_client()

        # Parse pagination parameters
        page, limit, offset = parse_pagination(data)
        logging.info(f"🔍 Fetching packages for {data}")
        logging.debug(f"Pagination - Page: {page}, Limit: {limit}, Offset: {offset}")

        # ✅ ใช้ DISTINCT เพื่อลดข้อมูลซ้ำ
        QUERY = """
        SELECT DISTINCT insurance_company AS company_name,
                        CAST(premium AS FLOAT64) AS premium,  -- ✅ แปลงเป็น FLOAT
                        repair_type,
                        insurance_type,
                        car_model,
                        car_brand,
                        car_model_year
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand
          AND car_model = @car_model
          AND car_model_year = @car_model_year
          AND repair_type = @repair_type
        ORDER BY premium ASC
        LIMIT @limit OFFSET @offset
        """
        
        # ✅ กำหนด query_parameters ให้ client ใช้
        query_parameters = [
            bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
            bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
            bigquery.ScalarQueryParameter("car_model_year", "STRING", car_model_year),
            bigquery.ScalarQueryParameter("repair_type", "STRING", repair_type),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset),
        ]

        job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
        query_job = client.query(QUERY, job_config=job_config)
        results = [dict(row) for row in query_job.result()]
        logging.info(f"✅ Retrieved {len(results)} packages.")

        # Log results if any
        if not results:
            logging.info("ℹ️ No packages found for the given criteria.")
            return jsonify({"results": [], "page": page, "total_pages": 0, "total_rows": 0}), 200

        # ✅ แก้ไข TOTAL_QUERY เพื่อคำนวณ pagination ให้ถูกต้อง
        TOTAL_QUERY = """
        SELECT COUNT(*) AS total_rows
        FROM (
            SELECT DISTINCT insurance_company, premium, repair_type, insurance_type, car_model, car_brand, car_model_year
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
            WHERE car_brand = @car_brand
              AND car_model = @car_model
              AND car_model_year = @car_model_year
              AND repair_type = @repair_type
        )
        """
        total_query_job = client.query(TOTAL_QUERY, job_config=bigquery.QueryJobConfig(query_parameters=query_parameters))
        total_rows = next(total_query_job.result()).get("total_rows", 0)
        total_pages = (total_rows + limit - 1) // limit  # Ceiling division for total pages

        # ✅ แปลง premium เป็น float (สำรอง ถ้า BigQuery ไม่แปลง)
        for result in results:
            if isinstance(result["premium"], Decimal):
                result["premium"] = float(result["premium"])

        # Prepare the response payload
        response = {
            "results": results,
            "page": page,
            "total_pages": total_pages,
            "total_rows": total_rows,
        }
        logging.debug(f"📦 Response: {response}")
        return jsonify(response), 200

    except ValueError as ve:
        logging.warning(f"❌ Validation Error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.error("❌ Error fetching packages.", exc_info=True)
        return handle_error("Failed to fetch packages", e)


@multi_step_search_bp.route('/available-options', methods=['GET'])
def get_available_options():
    car_brand = request.args.get("car_brand")
    car_model = request.args.get("car_model")
    car_submodel = request.args.get("car_submodel")
    year = request.args.get("year")

    try:
        client = get_bigquery_client()

        QUERY = """
        SELECT DISTINCT insurance_type, repair_type
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand
          AND car_model = @car_model
          AND (@car_submodel IS NULL OR car_submodel = @car_submodel)
          AND (@year IS NULL OR car_model_year = @year)
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
                bigquery.ScalarQueryParameter("car_submodel", "STRING", car_submodel),
                bigquery.ScalarQueryParameter("year", "STRING", year),
            ]
        )

        query_job = client.query(QUERY, job_config=job_config)
        raw_results = list(query_job.result())

        # Debug log
        print(f"📦 [BQ] Matched rows: {len(raw_results)}")

        insurance_map = {
            "1": "1", "2": "2", "2P": "2+", "2+": "2+", "3": "3", "3P": "3+", "3+": "3+"
        }
        repair_map = {
            "ซ่อมอู่": "ซ่อมอู่", "ซ่อมห้าง": "ซ่อมห้าง",
            "ซ่อมอู่ห้าง": "ซ่อมห้าง", "ซ่อมอู่ประกัน": "ซ่อมอู่"
        }

        insurance_types = sorted({insurance_map.get(r["insurance_type"]) for r in raw_results if r["insurance_type"] in insurance_map})
        repair_types = sorted({repair_map.get(r["repair_type"]) for r in raw_results if r["repair_type"] in repair_map})

        # fallback if empty
        if not insurance_types:
            insurance_types = ["1", "2+", "3+"]
        if not repair_types:
            repair_types = ["ซ่อมอู่", "ซ่อมห้าง"]

        return jsonify({
            "insurance_types": insurance_types,
            "repair_types": repair_types,
            "years": [year] if year else [],
        })

    except Exception as e:
        return handle_error("Failed to fetch available insurance/repair types", e)
