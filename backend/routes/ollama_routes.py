# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/ollama_routes.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/ollama_routes.py
from flask import Blueprint, request, jsonify, current_app
import requests
import logging
import re

ollama_bp = Blueprint("ollama", __name__)
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def contains_fabricated_price(text: str) -> bool:
    """
    ตรวจว่ามีตัวเลขราคาแบบ xx,xxx หรือไม่ → ใช้ flag ว่าอาจแต่งราคาเอง
    """
    return bool(re.search(r"\b\d{1,2},\d{3}\b", text))

@ollama_bp.route("/ask-ollama", methods=["POST"])
def ask_ollama():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()

        if not prompt:
            current_app.logger.warning("Received empty prompt")
            return jsonify({"error": "Missing prompt"}), 400

        current_app.logger.debug(f"📨 Prompt to Ollama: {prompt}")

        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        result = response.json()
        reply = result.get("response", "").strip() or "ขออภัยครับ พี่ยังไม่มีคำตอบให้ตอนนี้ 😓"
        current_app.logger.debug(f"✅ Ollama reply: {reply}")

        # 🛑 ตรวจจับว่ามีเบี้ยประกันในรูปแบบที่อาจแต่งเอง
        if contains_fabricated_price(reply):
            warning_msg = "⚠️ Ollama ตอบกลับพร้อมเบี้ยที่อาจไม่ยืนยันจากระบบจริง"
            current_app.logger.warning(warning_msg)
            return jsonify({
                "response": "Ollama ตอบกลับพร้อมเบี้ยที่อาจไม่ยืนยันจากระบบจริง — กำลังดึงข้อมูลจริงให้ครับ",
                "raw_response": reply,
                "warning": "fabricated_price_detected"
            }), 200

        # ✅ ตอบปกติ
        return jsonify({"response": reply}), 200

    except requests.exceptions.Timeout:
        current_app.logger.error("⏱️ Timeout while connecting to Ollama")
        return jsonify({"error": "Ollama connection timed out"}), 504

    except requests.exceptions.RequestException as req_err:
        current_app.logger.error(f"❌ Ollama connection error: {req_err}")
        return jsonify({"error": "Unable to reach Ollama backend"}), 503

    except Exception as e:
        current_app.logger.exception("❌ Internal server error")
        return jsonify({"error": "Unexpected server error"}), 500
