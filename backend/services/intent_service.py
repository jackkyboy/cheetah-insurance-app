# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/intent_service.py
# backend/services/intent_service.py
# backend/services/intent_service.py
from backend.utils.nlp import parseInsuranceQuery
from google.cloud import bigquery

# แยก company mapping ไว้ใช้ร่วมกับ gallery_routes ได้เลย
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

insurance_type_map = {
    "1": "1",
    "0": "0",
    "2": "%2+%",
    "2+": "%2+%",
    "2p": "%2+%",
    "3": "%3+%",
    "3+": "%3+%",
    "3p": "%3+%",
}

def handle_user_input(prompt, app):
    parsed = parseInsuranceQuery(prompt)

    if parsed.brand and parsed.model and parsed.year and parsed.insurance_type:
        client = app.extensions["bigquery_config"].client

        # normalize insurance_type: แปลง p → + และ lowercase
        ins_type = parsed.insurance_type.lower().replace('p', '+')

        # mapping insurance_type ให้ตรงกับ DB pattern
        insurance_type_like = insurance_type_map.get(ins_type, f"%{ins_type}%")

        query = """
            SELECT
                Insurance_company,
                car_brand,
                car_model,
                car_model_year,
                insurance_type,
                repair_type,
                premium
            FROM `cheetah-insurance-broker.insurance.insurance_data_center`
            WHERE TRIM(LOWER(car_brand)) = @brand
              AND TRIM(LOWER(car_model)) = @model
              AND TRIM(CAST(car_model_year AS STRING)) = @year
              AND LOWER(insurance_type) LIKE @insurance_type
            ORDER BY premium ASC
            LIMIT 10
        """

        job_config = bigquery.QueryJobConfig(query_parameters=[
            bigquery.ScalarQueryParameter("brand", "STRING", parsed.brand.lower().strip()),
            bigquery.ScalarQueryParameter("model", "STRING", parsed.model.lower().strip()),
            bigquery.ScalarQueryParameter("year", "STRING", str(parsed.year).strip()),
            bigquery.ScalarQueryParameter("insurance_type", "STRING", insurance_type_like),
        ])

        try:
            rows = [dict(row) for row in client.query(query, job_config=job_config).result()]

            if not rows:
                return {
                    "intent": "insurance_package_search",
                    "query": [parsed.brand, parsed.model, parsed.year, parsed.insurance_type],
                    "response": f"ไม่พบแพ็กเกจที่ตรงกับคำค้น ลองระบุยี่ห้อ/รุ่นใหม่อีกครั้งนะครับ 🙏",
                    "results": []
                }

            # เติมชื่อบริษัทเต็มและโลโก้ในผลลัพธ์
            for row in rows:
                comp_code = row.get("Insurance_company", "")
                info = get_company_info(comp_code)
                row["insurance_company"] = comp_code
                row["company_full_name"] = info["full_name"]
                row["company_logo"] = info["logo"]
                if "Insurance_company" in row:
                    del row["Insurance_company"]

            # สร้างข้อความสรุปบริษัท 5 รายการแรก พร้อมข้อมูลเสริมอธิบายประกันประเภท 3+
            summary = (
                f"หากคุณกำลังมองหาประกันรถ {parsed.brand.title()} {parsed.model.title()} ปี {parsed.year} "
                f"ประเภท {parsed.insurance_type}+, ฉันจะช่วยคุณหาได้! "
                "ตามข้อมูลของกรมธรรมประกันวินาศภัยแห่งประเทศไทย (TPI), "
                "ประกันรถประเภท 3+ จะมีค่าเบี้ยประกันที่สูงกว่าประกันประเภท 1 และ 2 "
                "แต่จะมีคณะกรรมการตรวจสอบและกำหนดเงื่อนไขที่เข้มงวดมากกว่า "
                f"สำหรับ {parsed.brand.title()} {parsed.model.title()} ปี {parsed.year} ประเภท {parsed.insurance_type}+ "
                "คุณสามารถหาประกันได้ที่บริษัทประกันวินาศภัยหลายแห่ง เช่น:"
            )
            company_texts = []
            for i, row in enumerate(rows[:5], 1):
                comp_name = row.get("company_full_name", "บริษัทประกัน")
                premium = row.get("premium", "ไม่ระบุราคา")
                cover_note = "คุ้มครอง 3 คันทุกคน (Driver, Passenger และ Pedestrian)"
                company_texts.append(f"{i}. {comp_name} - {cover_note} * ราคาประมาณ {premium} บาทต่อปี")

            full_response = summary + " " + " ".join(company_texts) + \
                " โปรดทราบว่าราคาและเงื่อนไขของประกันรถยนต์อาจเปลี่ยนแปลงได้ตลอดเวลา และคุณควรมาดูและเลือกประกันรถยนต์ที่เหมาะกับคุณเองมากกว่า หากคุณสนใจที่จะขอความช่วยเหลือเพิ่มเติม สามารถติดต่อสอบถามกับบริษัทประกันรถยนต์เหล่านี้ได้"

            return {
                "intent": "insurance_package_search",
                "query": [parsed.brand, parsed.model, parsed.year, parsed.insurance_type],
                "response": full_response,
                "results": rows
            }

        except Exception as e:
            app.logger.error(f"❌ BigQuery query failed: {e}")
            return {
                "response": "เกิดข้อผิดพลาดขณะค้นหาข้อมูลจากฐานข้อมูล",
                "intent": "error",
                "error": str(e)
            }

    return {
        "response": "⚠️ ยังไม่สามารถเข้าใจคำถามได้ชัดเจน",
        "intent": "fallback"
    }
