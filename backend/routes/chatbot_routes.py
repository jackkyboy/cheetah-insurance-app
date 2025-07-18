# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/chatbot_routes.py
# /backend/routes/chatbot_routes.py
import re
import requests
from flask import Blueprint, request, jsonify
from backend.routes.bigquery_routes import map_insurance_type_group

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


def parse_insurance_query(message):
    brand_match = re.search(r"(toyota|honda|nissan|isuzu|mazda|ford|byd|mg)", message, re.IGNORECASE)
    model_match = re.search(r"(yaris|civic|dmax|march|cx[- ]?5|ranger|atto|zs)", message, re.IGNORECASE)
    year_match = re.search(r"(20\d{2})", message)
    type_match = re.search(r"(ชั้น\s?1|ชั้น\s?2\+?|ชั้น\s?3\+?|ชั้น\s?3)", message)
    repair_match = re.search(r"(ซ่อมห้าง|ซ่อมอู่)", message)

    if not (brand_match and model_match and year_match and type_match and repair_match):
        return None

    return {
        "car_brand": brand_match.group(1).upper(),
        "car_model": model_match.group(1).upper().replace(" ", "").replace("-", ""),
        "car_model_year": int(year_match.group(1)),
        "insurance_type": type_match.group(1).replace("ชั้น", "").strip(),
        "repair_type": "ซ่อมห้าง" if "ห้าง" in repair_match.group(1) else "ซ่อมอู่",
    }


@chatbot_bp.route("/ask", methods=["POST"])
def ask_chatbot():
    try:
        message = request.json.get("message", "")
        if not message:
            return jsonify({"error": "❌ ไม่พบข้อความ"}), 400

        print(f"📩 คำถามผู้ใช้: {message}")
        parsed = parse_insurance_query(message)
        if not parsed:
            return jsonify({"answer": "❌ ไม่สามารถวิเคราะห์คำถามได้ กรุณาระบุยี่ห้อ รุ่น ปี ชั้น ซ่อมอู่/ห้าง"}), 200

        insurance_type_group = map_insurance_type_group(parsed["insurance_type"])
        payload = {
            "car_brand": parsed["car_brand"],
            "car_model": parsed["car_model"],
            "car_model_year": str(parsed["car_model_year"]),
            "insurance_type": parsed["insurance_type"],
            "car_submodel": "",
            "page": 1,
            "limit": 5
        }

        # เรียกใช้ endpoint ของคุณเองภายใน Flask หรือผ่าน HTTP ถ้าแยกโปรเซส
        from backend.routes.bigquery_routes import compare_insurance
        with request.environ:
            resp = compare_insurance()
            return resp

    except Exception as e:
        return jsonify({"error": f"❌ ระบบขัดข้อง: {str(e)}"}), 500
