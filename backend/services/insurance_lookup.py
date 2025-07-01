import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# 📌 ใช้ scope เพื่อเชื่อมต่อ Google Sheets API
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 📂 Path ไปยัง credentials JSON
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "../config/credentials.json")

# 🧠 ใส่ Google Sheet ID ของพี่ตรงนี้
SPREADSHEET_ID = "https://docs.google.com/spreadsheets/d/1jjoZChAO82xVn27jJ1XeEgs-VGkVhfSmOuTTKjH5iOY/edit?gid=607349088#gid=607349088"
SHEET_NAME = "insurance_data_center"

def find_premium(brand, model, year, insurance_type, repair_type):
    try:
        # 🔐 Auth + connect
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

        # 🔍 อ่านข้อมูลทั้งหมด
        data = sheet.get_all_records()

        for row in data:
            if (
                row["car_brand"].strip().lower() == brand.strip().lower() and
                row["car_model"].strip().lower() == model.strip().lower() and
                str(row["car_model_year"]) == str(year) and
                row["insurance_type"].strip() == insurance_type.strip() and
                row["repair_type"].strip() == repair_type.strip()
            ):
                return str(row["premium_amount"])

    except Exception as e:
        print(f"❌ Error in find_premium(): {e}")
        return None

    return None
