# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/chatbot_routes.py

import os
import time
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# === Flask Blueprint ===
chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")

# === Load API Key ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Upload CSV ===
csv_path = "/Users/apichet/Downloads/insurance_data.csv"
with open(csv_path, "rb") as f:
    uploaded_file = client.files.create(file=f, purpose="assistants")
file_id = uploaded_file.id
print(f"📂 Uploaded file ID: {file_id}")

# === Create Assistant ===
assistant = client.beta.assistants.create(
    name="พี่เสือชีต้า",
    instructions="""
คุณคือผู้ช่วยด้านประกันภัยรถยนต์ชื่อ 'พี่เสือชีต้า' 🐆
คุณได้รับไฟล์ CSV ที่มีคอลัมน์: ['Insurance_company', 'package_code', 'car_brand', 'car_model', 'car_submodel',
'car_model_year', 'insurance_type', 'repair_type', 'premium']

✅ วิธีทำงาน:
1. โหลดไฟล์ด้วย pandas:
   import pandas as pd
   df = pd.read_csv("/mnt/data/insurance_data.csv")
2. แสดง df.head() เพื่อยืนยันว่าโหลดไฟล์ได้
3. วิเคราะห์คำถาม เช่น:
   - "Yaris ปี 2022 ชั้น 1 ซ่อมห้าง" → brand=TOYOTA, model=YARIS, year=2022, insurance_type=1, repair_type='ซ่อมห้าง'
4. จากนั้น query ด้วย pandas:
   result = df[
       (df['car_brand'].str.lower() == 'toyota') &
       (df['car_model'].str.lower() == 'yaris') &
       (df['car_model_year'] == 2022) &
       (df['insurance_type'] == 1) &
       (df['repair_type'] == 'ซ่อมห้าง')
   ]
5. ถ้า result ว่าง:
   print("❌ ไม่พบข้อมูลในระบบ")
6. ถ้าเจอ:
   print(result[['car_submodel', 'premium', 'repair_type']])
ห้ามแต่งข้อมูลเองเด็ดขาด! ต้องตอบด้วย print(...) เท่านั้น
""",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o"
)
assistant_id = assistant.id
print(f"✅ Assistant ID: {assistant_id}")

# === Create Thread ===
thread = client.beta.threads.create()
thread_id = thread.id
print(f"🧵 Thread ID: {thread_id}")

# === Flask API Endpoint ===
@chatbot_bp.route("/ask", methods=["POST"])
def ask_from_api():
    try:
        question = request.json.get("message", "")
        if not question:
            return jsonify({"error": "No message provided"}), 400

        print(f"💬 คำถามจาก API: {question}")

        # ส่ง message พร้อมแนบไฟล์
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question,
            attachments=[
                {
                    "file_id": file_id,
                    "tools": [{"type": "code_interpreter"}]
                }
            ]
        )

        # รัน Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            instructions="ใช้เฉพาะข้อมูลในไฟล์ CSV นี้ ห้ามแต่งเอง"
        )

        # Poll รอคำตอบ
        start_time = time.time()
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status in ['completed', 'failed']:
                break
            if time.time() - start_time > 30:
                return jsonify({"error": "⏰ Timeout"}), 408
            time.sleep(2)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        for m in messages.data:
            if m.role == "assistant":
                for part in m.content:
                    if hasattr(part, "text") and part.text.value.strip():
                        return jsonify({"answer": part.text.value.strip()})

        return jsonify({"error": "❌ ไม่มีคำตอบกลับจาก Assistant"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
