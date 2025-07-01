# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/car_options_routes.py
from flask import Blueprint, request, jsonify
from google.cloud import bigquery
import logging
from flask import current_app


# Initialize Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Initialize Blueprint
car_options_bp = Blueprint("car_options", __name__)

# Global BigQuery Client
bigquery_client = None

# Mapping insurance companies to their logos
PARTNER_LOGOS = {
    "MTI": "/logos/MTI-logo.svg",
    "Viriyah": "/logos/VIRIYAH-logo.svg",
    "Chubb": "/logos/CHUBB-logo.svg",
    "Tokio Marine": "/logos/TOKIO-MARINE-logo.svg",
    "Ergo": "/logos/ERGO-logo.svg",
}



from flask import current_app

def get_bigquery_client():
    """
    Retrieves the BigQuery client from the current Flask app context.
    """
    try:
        bq_config = current_app.extensions.get("bigquery_config")
        if not bq_config:
            raise RuntimeError("BigQueryConfig not initialized in app.extensions")
        return bq_config.client
    except Exception as e:
        logger.error(f"❌ Error retrieving BigQuery client: {e}")
        raise RuntimeError("Failed to retrieve BigQuery client.")


@car_options_bp.route('/packages_with_logos', methods=['GET'])
def get_packages_with_logos():
    """
    Fetch insurance companies and their logos with pagination support.
    """
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 5))
        offset = (page - 1) * limit

        if page < 1 or limit < 1:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        client = get_bigquery_client()

        # Query insurance companies with pagination
        query = """
        SELECT DISTINCT insurance_company
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE insurance_company IS NOT NULL
        ORDER BY insurance_company
        LIMIT @limit OFFSET @offset
        """
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset),
                ]
            ),
        )
        results = query_job.result()

        # Map companies to their logos
        packages = [
            {
                "insurance_company": row["insurance_company"],
                "logo_url": PARTNER_LOGOS.get(row["insurance_company"], "/static/logos/default-logo.svg"),
            }
            for row in results
        ]

        # Query total number of insurance companies
        total_query = """
        SELECT COUNT(DISTINCT insurance_company) AS total
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        """
        total_result = client.query(total_query).result()
        total_rows = next(total_result)["total"]

        total_pages = (total_rows + limit - 1) // limit

        logger.debug(f"Fetched {len(packages)} packages with logos (Page {page}/{total_pages}).")
        return jsonify({
            "results": packages,
            "page": page,
            "total_pages": total_pages,
        }), 200

    except Exception as e:
        logger.error(f"Error fetching packages with logos: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@car_options_bp.route('/car_brands', methods=['GET'])
def get_car_brands():
    """
    Fetch car brands with optional pagination.
    """
    try:
        client = get_bigquery_client()

        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 50))
        offset = (page - 1) * limit

        if page < 1 or limit < 1:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        query = """
        SELECT DISTINCT car_brand
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        ORDER BY car_brand
        LIMIT @limit OFFSET @offset
        """
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                    bigquery.ScalarQueryParameter("offset", "INT64", offset),
                ]
            ),
        )
        results = query_job.result()

        car_brands = [row.get("car_brand", "N/A") for row in results]

        # Count total car brands for pagination
        count_query = """
        SELECT COUNT(DISTINCT car_brand) AS total
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        """
        total_result = client.query(count_query).result()
        total_rows = next(total_result)["total"]
        total_pages = (total_rows + limit - 1) // limit

        logger.info(f"Fetched {len(car_brands)} car brands (Page {page}/{total_pages}).")
        return jsonify({"results": car_brands, "page": page, "total_pages": total_pages}), 200

    except Exception as e:
        logger.error(f"Error fetching car brands: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



@car_options_bp.route('/models', methods=['GET'])
def get_car_models():
    """
    Fetch car models for a given car brand.
    """
    car_brand = request.args.get('brand')

    if not car_brand:
        return jsonify({"error": "Car brand is required"}), 400

    try:
        client = get_bigquery_client()
        query = """
        SELECT DISTINCT car_model
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand
        ORDER BY car_model
        """
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand)]
            ),
        )
        results = query_job.result()
        car_models = [row.get("car_model", "N/A") for row in results]

        logger.debug(f"Fetched {len(car_models)} models for {car_brand}.")
        return jsonify({"results": car_models}), 200
    except Exception as e:
        logger.error(f"Error fetching car models: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@car_options_bp.route('/submodels', methods=['GET'])
def get_car_submodels():
    """
    Fetch car submodels for a given car brand and model.
    """
    car_brand = request.args.get('brand')
    car_model = request.args.get('model')

    if not car_brand or not car_model:
        return jsonify({"error": "Car brand and model are required"}), 400

    try:
        client = get_bigquery_client()
        query = """
        SELECT DISTINCT car_submodel
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand AND car_model = @car_model
        ORDER BY car_submodel
        """
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                    bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
                ]
            ),
        )
        results = query_job.result()
        car_submodels = [row.get("car_submodel", "N/A") for row in results]

        logger.debug(f"Fetched {len(car_submodels)} submodels for {car_brand} {car_model}.")
        return jsonify({"results": car_submodels}), 200
    except Exception as e:
        logger.error(f"Error fetching car submodels: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@car_options_bp.route('/years', methods=['GET'])
def get_car_years():
    """
    Fetch car years for a given car brand, model, and submodel.
    """
    car_brand = request.args.get('brand')
    car_model = request.args.get('model')
    car_submodel = request.args.get('submodel', "N/A")

    if not car_brand or not car_model:
        return jsonify({"error": "Car brand and model are required"}), 400

    try:
        client = get_bigquery_client()
        query = """
        SELECT DISTINCT car_model_year
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE car_brand = @car_brand AND car_model = @car_model
        AND (@car_submodel = 'N/A' OR car_submodel = @car_submodel)
        ORDER BY car_model_year
        """
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
                    bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
                    bigquery.ScalarQueryParameter("car_submodel", "STRING", car_submodel),
                ]
            ),
        )
        results = query_job.result()
        car_years = [row.get("car_model_year", "N/A") for row in results]

        logger.debug(f"Fetched {len(car_years)} years for {car_brand} {car_model} {car_submodel}.")
        return jsonify({"results": car_years}), 200
    except Exception as e:
        logger.error(f"Error fetching car years: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



@car_options_bp.route('/cm_required', methods=['GET'], endpoint="car_options_get_cm_required")
def get_cm_required():
    """
    ตรวจสอบข้อมูลภาคบังคับ (CM) สำหรับ CMI
    """
    try:
        # Initialize BigQuery client
        client = get_bigquery_client()

        # Query to fetch required CM data
        query = """
        SELECT DISTINCT 
            IFNULL(car_brand, 'N/A') AS car_brand, 
            IFNULL(car_model, 'N/A') AS car_model, 
            IFNULL(insurance_type, 'N/A') AS insurance_type
        FROM `cheetah-insurance-broker.insurance.insurance_cm_data`
        ORDER BY car_brand, car_model
        """
        query_job = client.query(query)
        results = query_job.result()

        # Extract CM requirements
        cm_data = [
            {
                "car_brand": row["car_brand"],
                "car_model": row["car_model"],
                "insurance_type": row["insurance_type"],
            }
            for row in results
        ]

        # Log the fetched data count
        logger.debug(f"Fetched {len(cm_data)} CM requirements.")
        return jsonify({"results": cm_data}), 200

    except Exception as e:
        # Log error and return a 500 response
        logger.error(f"Error fetching CM data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/car_options_routes.py
@car_options_bp.route('/fetch_packages', methods=['POST'])
def fetch_cmi_packages():
    """
    Fetch packages for CMI (Mandatory Insurance) based on frontend input.
    """
    try:
        # รับข้อมูลจาก frontend
        data = request.get_json()

        car_brand = data.get("car_brand")
        car_model = data.get("car_model")
        car_model_year = data.get("car_model_year")
        repair_type = data.get("repair_type", "ซ่อมอู่")  # Default "ซ่อมอู่"
        try:
            limit = int(data.get("limit", 10))  # Default limit
            offset = int(data.get("offset", 0))  # Default offset
        except ValueError:
            return jsonify({"error": "Invalid limit or offset parameter"}), 400

        # ตรวจสอบ input ว่าครบถ้วนหรือไม่
        if not all([car_brand, car_model, car_model_year]):
            return jsonify({"error": "Missing required parameters"}), 400

        # Query BigQuery
        query = """
        SELECT 
            IFNULL(insurance_company, "Unknown") AS company_name,
            IFNULL(premium, 0.0) AS premium,
            IFNULL(repair_type, "Unknown") AS repair_type,
            IFNULL(insurance_type, "Unknown") AS insurance_type,
            IFNULL(car_model, "Unknown") AS car_model,
            IFNULL(car_brand, "Unknown") AS car_brand,
            IFNULL(car_model_year, "Unknown") AS car_model_year,
            IFNULL(package_code, "Unknown") AS package_code
        FROM 
            `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE 
            car_brand = @car_brand
            AND car_model = @car_model
            AND car_model_year = @car_model_year
            AND repair_type = @repair_type
        ORDER BY 
            premium ASC
        LIMIT @limit OFFSET @offset
        """

        # สร้าง Query Parameters
        query_parameters = [
            bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand),
            bigquery.ScalarQueryParameter("car_model", "STRING", car_model),
            bigquery.ScalarQueryParameter("car_model_year", "STRING", car_model_year),
            bigquery.ScalarQueryParameter("repair_type", "STRING", repair_type),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset),
        ]

        # ส่งคำสั่ง Query ไปที่ BigQuery
        client = get_bigquery_client()
        query_job = client.query(
            query,
            job_config=bigquery.QueryJobConfig(query_parameters=query_parameters)
        )
        results = query_job.result()

        # จัดรูปแบบผลลัพธ์และลบข้อมูลซ้ำ
        unique_packages = {}
        for row in results:
            package_code = row["package_code"]
            if package_code not in unique_packages:
                unique_packages[package_code] = {
                    "company_name": row["company_name"],
                    "premium": float(row["premium"]),
                    "repair_type": row["repair_type"],
                    "insurance_type": row["insurance_type"],
                    "car_model": row["car_model"],
                    "car_brand": row["car_brand"],
                    "car_model_year": row["car_model_year"],
                    "package_code": package_code,
                }

        packages = list(unique_packages.values())

        # ตรวจสอบว่ามีข้อมูลหรือไม่
        if not packages:
            return jsonify({"message": "No packages found for the given criteria"}), 404

        logger.info(f"Fetched {len(packages)} packages for {car_brand} {car_model} ({car_model_year}). Example: {packages[0] if packages else 'No data'}")
        return jsonify({"results": packages}), 200

    except Exception as e:
        logger.error(f"Error fetching packages: {e}")
        return jsonify({"error": "Internal Server Error"}), 500








@car_options_bp.route('/get_insurance_companies', methods=['GET'])
def get_insurance_companies():
    """
    ดึงข้อมูลบริษัทประกันภัยทั้งหมด
    """
    try:
        # Initialize BigQuery client
        client = get_bigquery_client()

        # Query for insurance companies
        query = """
        SELECT DISTINCT insurance_company
        FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        WHERE insurance_company IS NOT NULL
        ORDER BY insurance_company
        """
        query_job = client.query(query)
        results = query_job.result()

        # Map results
        insurance_companies = [row["insurance_company"] for row in results]

        # Log the count
        logger.debug(f"Fetched {len(insurance_companies)} insurance companies.")
        return jsonify({"results": insurance_companies}), 200

    except Exception as e:
        logger.error(f"Error fetching insurance companies: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



