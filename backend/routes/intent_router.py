

# ✅ /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/intent_router.py
# /backend/routes/intent_router.py

# /backend/routes/intent_router.py

from flask import Blueprint, request, jsonify, current_app
from google.cloud import bigquery
from backend.services.bigquery_service import BigQueryService
from backend.services.ollama_service import askOllamaWithData, parseOllamaToPackages

# กำหนด config project/location ตามจริง
BQ_PROJECT_ID = "cheetah-insurance-broker"
BQ_LOCATION = "asia-southeast1"

# สร้าง instance BigQueryService
bq_service = BigQueryService(project_id=BQ_PROJECT_ID, location=BQ_LOCATION)

intent_bp = Blueprint("intent_router", __name__, url_prefix="/api/intent")


# 🔍 โหลด package_code จาก BigQuery
def get_valid_package_codes():
    try:
        query = """
            SELECT DISTINCT package_code
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
        """
        result = bq_service.execute_query(query)
        return {row["package_code"].strip().lower() for row in result if row.get("package_code")}
    except Exception as e:
        current_app.logger.error(f"❌ Failed to load valid package codes: {e}")
        return set()


# ✅ ตรวจว่า description จาก Ollama ตรงกับ package_code จริงใน BigQuery หรือไม่
def validate_ollama_packages(packages_from_ollama, valid_package_codes: set[str]):
    matched = []
    unmatched = []

    for pkg in packages_from_ollama:
        desc = pkg.get("description", "").lower()
        has_match = any(code in desc for code in valid_package_codes)
        if has_match:
            matched.append(pkg)
        else:
            unmatched.append(pkg)
    return matched, unmatched


@intent_bp.route("/handle", methods=["POST"])
def handle_intent():
    try:
        data = request.get_json(force=True)
        prompt = (data.get("prompt") or "").strip()

        if not prompt:
            current_app.logger.warning("Missing prompt in request")
            return jsonify({"error": "Missing prompt"}), 400

        current_app.logger.debug(f"📩 Prompt received: {prompt}")

        from backend.utils.nlp import parseInsuranceQuery

        parsed = parseInsuranceQuery(prompt)
        brand = getattr(parsed, "brand", None)
        model = getattr(parsed, "model", None)
        year = getattr(parsed, "year", None)
        insurance_type = getattr(parsed, "insurance_type", None)

        # ✅ CASE 1: ตอบจาก BigQuery โดยตรง
        if brand and model and year and insurance_type:
            try:
                query = """
                    SELECT Insurance_company, car_brand, car_model, car_model_year,
                           insurance_type, repair_type, premium
                    FROM `cheetah-insurance-broker.insurance.insurance_data_center`
                    WHERE TRIM(LOWER(car_brand)) = @brand
                      AND TRIM(LOWER(car_model)) = @model
                      AND TRIM(CAST(car_model_year AS STRING)) = @year
                      AND LOWER(insurance_type) LIKE @insurance_type
                    ORDER BY premium ASC
                    LIMIT 10
                """
                parameters = [
                    bigquery.ScalarQueryParameter("brand", "STRING", brand.lower()),
                    bigquery.ScalarQueryParameter("model", "STRING", model.lower()),
                    bigquery.ScalarQueryParameter("year", "STRING", year),
                    bigquery.ScalarQueryParameter("insurance_type", "STRING", f"%{insurance_type.lower()}%"),
                ]
                results, status = bq_service.execute_query_with_count(query, parameters)
                if status == 200 and results.get("data"):
                    return jsonify({
                        "intent": "insurance_package_search",
                        "response": f"พบบริษัทประกัน {len(results['data'])} รายการที่ตรงกับ {brand} {model} ปี {year}",
                        "results": results["data"],
                    })

            except Exception as e:
                current_app.logger.error(f"BigQuery error: {e}")
                return jsonify({
                    "intent": "error",
                    "response": "เกิดข้อผิดพลาดขณะค้นหาข้อมูลจากฐานข้อมูล",
                    "error": str(e),
                }), 500

        # ✅ CASE 2: ตอบจาก Ollama (fallback)
        try:
            ollama_resp = askOllamaWithData(prompt)
            packages = parseOllamaToPackages(ollama_resp)

            # โหลดรายการแพ็กเกจจริงจาก BigQuery
            valid_codes = get_valid_package_codes()

            # ตรวจสอบว่าแพ็กเกจของ Ollama ตรงกับของจริงหรือไม่
            verified_packages, unmatched_packages = validate_ollama_packages(packages, valid_codes)

            if not verified_packages:
                text_resp = "ไม่มีข้อมูลแพ็กเกจที่ตรงกับฐานข้อมูลจริงครับ 🙏"
            else:
                text_resp = f"พบแพ็กเกจที่ตรงกับระบบจริง {len(verified_packages)} รายการ"

                # ✅ สร้างชื่อบริษัทจริงจาก BigQuery ที่ได้จาก verified packages
                companies_in_real_data = {
                    pkg.get("insurance_company", "").strip().lower()
                    for pkg in verified_packages
                }

                # ✅ รายชื่อบริษัททั้งหมดที่ Ollama อาจตอบ
                known_companies = [
                    "ชับบ์", "ergo", "เมืองไทยประกันภัย", "วิริยะ",
                    "axa", "ทิพยประกันภัย", "กรุงไทยพานิช",
                    "msig", "โตเกียวมารีน"
                ]

                # ✅ ตรวจสอบว่าใครไม่มีข้อมูลในระบบ
                missing_companies = [
                    name for name in known_companies if name.lower() not in companies_in_real_data
                ]

                # ✅ เพิ่มข้อความตอบกลับ
                if missing_companies:
                    fallback_lines = [f"* {name}: ไม่มีข้อมูลในระบบ" for name in missing_companies]
                    text_resp += "\n\n" + "\n".join(fallback_lines)


            return jsonify({
                "intent": "insurance_package_search_fallback",
                "response": text_resp,
                "results": verified_packages,
                "unmatched": unmatched_packages,
                "raw": ollama_resp,
            })

        except Exception as e:
            current_app.logger.error(f"Ollama error: {e}")
            return jsonify({
                "intent": "error",
                "response": "เกิดข้อผิดพลาดขณะประมวลผลคำถาม",
                "error": str(e),
            }), 500

    except Exception as e:
        current_app.logger.exception("❌ Intent handling failed")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
        }), 500
