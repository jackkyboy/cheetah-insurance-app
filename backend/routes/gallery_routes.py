# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/gallery_routes.py
# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/gallery_routes.py
# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/gallery_routes.py
# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/gallery_routes.py
# /backend/routes/gallery_routes.py
# /backend/routes/gallery_routes.py
from flask import request, jsonify, current_app, Blueprint
from google.cloud import bigquery

gallery_api_bp = Blueprint("gallery_api", __name__)

# ✅ Mapping: short code → full name + logo
company_mapping = {
    "ergo": {
        "full_name": "บริษัท เออร์โกประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
        "logo": "/gallery_logos/partners/ERGO-logo.svg"
    },
    "chubb": {
        "full_name": "บริษัท ชับบ์สามัคคีประกันภัย จำกัด (มหาชน)",
        "logo": "/gallery_logos/partners/CHUBB-logo.svg"
    },
    "tokio marine": {
        "full_name": "บริษัท คุ้มภัยโตเกียวมารีนประกันภัย (ประเทศไทย) จำกัด (มหาชน)",
        "logo": "/gallery_logos/partners/TKI-logo.svg"
    },
    "viriyah": {
        "full_name": "บริษัท วิริยะประกันภัย จำกัด (มหาชน)",
        "logo": "/gallery_logos/partners/VIRIYAH-logo.svg"
    },
    "mti": {
        "full_name": "บริษัท เมืองไทยประกันภัย จำกัด (มหาชน)",
        "logo": "/gallery_logos/partners/MTI-logo.svg"
    }
}

def get_company_info(code: str):
    normalized = (code or "").strip().lower()
    return company_mapping.get(normalized, {
        "full_name": code,
        "logo": "/gallery_logos/partners/default-logo.svg"
    })

def reverse_company_lookup(full_name: str):
    full_name = (full_name or "").strip()
    for code, info in company_mapping.items():
        if info["full_name"] == full_name:
            return code
    return None

@gallery_api_bp.route("/packages", methods=["GET"])
def get_packages():
    try:
        bq_service = current_app.extensions.get("bigquery_service")
        if not bq_service:
            current_app.logger.error("❌ BigQueryService not registered")
            return jsonify({"error": "BigQueryService not available"}), 500

        client = bq_service.client

        car_brand = request.args.get("brand")
        car_model = request.args.get("model")
        insurance_type = request.args.get("type")
        car_year_raw = request.args.get("year")

        # ✅ Normalize input
        raw_company_input = request.args.get("company", "").strip()
        company_code = reverse_company_lookup(raw_company_input) or raw_company_input.strip().lower()

        limit = int(request.args.get("limit", 30))
        offset = int(request.args.get("offset", 0))

        where_clauses = ["premium IS NOT NULL", "premium > 1000"]
        if car_brand:
            where_clauses.append("TRIM(LOWER(car_brand)) = @car_brand")
        if car_model:
            where_clauses.append("TRIM(LOWER(car_model)) = @car_model")
        if insurance_type:
            where_clauses.append("TRIM(LOWER(insurance_type)) LIKE @insurance_type")
        if car_year_raw and car_year_raw.strip().isdigit():
            where_clauses.append("TRIM(CAST(car_model_year AS STRING)) = @car_year")
        elif car_year_raw:
            current_app.logger.warning(f"⚠️ Invalid car_year received: {car_year_raw}")
        if company_code:
            where_clauses.append("TRIM(LOWER(Insurance_company)) = @company")

        where_sql = " AND ".join(where_clauses)

        query = f"""
            SELECT
                Insurance_company,
                package_code,
                car_brand,
                car_model,
                car_submodel,
                car_model_year,
                insurance_type,
                repair_type,
                premium,
                cmi_amount,
                liability_per_person,
                liability_per_event,
                liability_property,
                liability_deductible,
                own_damage,
                own_theft_fire_damage,
                coverage_driver_death,
                covearage_passenger_death,
                coverage_medical_expense,
                coverage_bail_bond
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
            WHERE {where_sql}
            ORDER BY premium ASC
            LIMIT @limit OFFSET @offset
        """

        params = [
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
            bigquery.ScalarQueryParameter("offset", "INT64", offset),
        ]
        if car_brand:
            params.append(bigquery.ScalarQueryParameter("car_brand", "STRING", car_brand.strip().lower()))
        if car_model:
            params.append(bigquery.ScalarQueryParameter("car_model", "STRING", car_model.strip().lower()))
        if insurance_type:
            params.append(bigquery.ScalarQueryParameter("insurance_type", "STRING", f"%{insurance_type.strip().lower()}%"))
        if car_year_raw and car_year_raw.strip().isdigit():
            params.append(bigquery.ScalarQueryParameter("car_year", "STRING", car_year_raw.strip()))
        if company_code:
            params.append(bigquery.ScalarQueryParameter("company", "STRING", company_code))

        job_config = bigquery.QueryJobConfig(query_parameters=params)
        rows = [dict(row) for row in client.query(query, job_config=job_config).result()]

        for row in rows:
            raw_company_name = row.pop("Insurance_company", "")
            row["insurance_company"] = raw_company_name
            normalized_code = (raw_company_name or "").strip().lower()
            info = get_company_info(normalized_code)
            row["company_full_name"] = info["full_name"]
            row["company_logo"] = info["logo"]

        return jsonify({"message": "Filtered packages fetched", "results": rows})

    except Exception as e:
        current_app.logger.error(f"❌ Error in get_packages: {e}")
        return jsonify({"error": str(e)}), 500







@gallery_api_bp.route("/car-models", methods=["GET"])
def get_car_models():
    try:
        client = current_app.extensions["bigquery_service"].client
        brand = (request.args.get("brand") or "").strip()

        if not brand:
            return jsonify({"error": "brand is required"}), 400

        query = """
            SELECT DISTINCT TRIM(car_model) AS car_model
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
            WHERE TRIM(LOWER(car_brand)) = @brand
              AND car_model IS NOT NULL
            ORDER BY car_model
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand", "STRING", brand.lower())
            ]
        )

        results = [row.car_model for row in client.query(query, job_config=job_config).result()]
        return jsonify({"models": results})

    except Exception as e:
        current_app.logger.error(f"❌ Error in /car-models: {e}")
        return jsonify({"error": str(e)}), 500




# query เพื่อดึงปีของรุ่นรถที่มีในฐานข้อมูล
@gallery_api_bp.route("/model-years", methods=["GET"])
def get_model_years():
    try:
        client = current_app.extensions["bigquery_config"].client
        brand = request.args.get("brand")
        model = request.args.get("model")

        if not brand or not model:
            return jsonify({"error": "brand and model are required"}), 400

        query = """
            SELECT DISTINCT CAST(car_model_year AS STRING) AS car_model_year
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
            WHERE TRIM(LOWER(car_brand)) = @brand
              AND TRIM(LOWER(car_model)) = @model
              AND car_model_year IS NOT NULL
            ORDER BY car_model_year DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("brand", "STRING", brand.strip().lower()),
                bigquery.ScalarQueryParameter("model", "STRING", model.strip().lower()),
            ]
        )

        results = [row.car_model_year for row in client.query(query, job_config=job_config).result()]
        return jsonify({"years": results})

    except Exception as e:
        current_app.logger.error(f"❌ Error in /model-years: {e}")
        return jsonify({"error": str(e)}), 500
