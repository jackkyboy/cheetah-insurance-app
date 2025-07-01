# routes/line_webhook.py
from flask import Blueprint, request, jsonify
import re
import requests
from backend.services.insurance_lookup import find_premium


line_webhook = Blueprint('line_webhook', __name__)

LINE_CHANNEL_ACCESS_TOKEN = 'cb93d5c62e696203d77c9000ba5c0f85'

@line_webhook.route('/webhook', methods=['POST'])
def webhook():
    try:
        body = request.get_json()
        events = body.get("events", [])
        for event in events:
            reply_token = event['replyToken']
            user_text = event['message']['text']

            match = re.match(r'(\w+)\s+(\w+)\s+ปี\s+(\d{4})\s+.*ชั้น\s?([123])', user_text)
            if not match:
                return reply(reply_token, "พิมพ์ให้ครบ เช่น Mazda 2 ปี 2020 ชั้น 1")

            car_brand = match.group(1).title()
            car_model = match.group(2)
            car_year = match.group(3)
            insurance_type = f"ชั้น {match.group(4)}"
            repair_type = "ซ่อมอู่"

            premium = find_premium(car_brand, car_model, car_year, insurance_type, repair_type)
            msg = f"💡 เบี้ยประกัน {car_brand} {car_model} ปี {car_year} = {premium} บาท/ปี ✅" if premium else "ไม่พบข้อมูลครับ"
            return reply(reply_token, msg)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return jsonify({'status': 'error'}), 500

def reply(token, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": token,
        "messages": [{"type": "text", "text": text}]
    }
    r = requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=payload)
    return jsonify({"status": "ok"})
