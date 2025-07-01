# /Users/apichet/Downloads/cheetah-insurance-app/routes/bigquery_policy_routes.py
from flask import Blueprint, request, jsonify


bigquery_policy_bp = Blueprint("bigquery_policy", __name__)

# ตั้งค่า BigQuery Service
bigquery_service = BigQueryService(
    project_id="cheetah-insurance-broker",
    location="asia-southeast1"
)

@bigquery_policy_bp.route("/api/bigquery/policies", methods=["GET"])
def get_policies():
    """
    ดึงข้อมูลกรมธรรม์จาก BigQuery
    """
    try:
        # รับพารามิเตอร์จาก Query String
        insurance_company = request.args.get('insurance_company')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # ตรวจสอบพารามิเตอร์ที่จำเป็น
        if not insurance_company:
            return jsonify({"error": "insurance_company is required"}), 400

        # สร้าง Query
        QUERY = """
        SELECT *
        FROM `cheetah-insurance-broker.insurance.policies`
        WHERE LOWER(insurance_company) = LOWER(@insurance_company)
        """
        parameters = [
            bigquery.ScalarQueryParameter("insurance_company", "STRING", insurance_company)
        ]

        # เพิ่มช่วงวันที่หากกำหนด
        if start_date and end_date:
            QUERY += " AND DATE(request_date) BETWEEN @start_date AND @end_date"
            parameters.append(bigquery.ScalarQueryParameter("start_date", "DATE", start_date))
            parameters.append(bigquery.ScalarQueryParameter("end_date", "DATE", end_date))

        # เรียกใช้ BigQuery Service
        data, status_code = bigquery_service.execute_query(QUERY, parameters)
        return jsonify(data), status_code

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
