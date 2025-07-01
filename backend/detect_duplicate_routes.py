# /Users/apichet/Downloads/cheetah-insurance-app/backend/routes/detect_duplicate_routes.py
import os
import re
from collections import Counter

# Path ของโฟลเดอร์ backend/routes/
ROUTES_DIR = './backend/routes'

# หา decorator @user_bp.route(...) ที่ซ้ำกัน
route_pattern = re.compile(r'@(\w+_bp)\.route\(["\'](.*?)["\']')

# เก็บ endpoint ทั้งหมด
all_endpoints = []

# เดินผ่านไฟล์ทั้งหมดใน routes directory
for root, dirs, files in os.walk(ROUTES_DIR):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = route_pattern.findall(content)
                for match in matches:
                    blueprint, endpoint = match
                    all_endpoints.append((blueprint, endpoint, file_path))

# ตรวจหา endpoint ที่ซ้ำ
endpoint_counter = Counter(all_endpoints)
duplicates = [ep for ep, count in endpoint_counter.items() if count > 1]

# แสดงผลลัพธ์
if duplicates:
    print("🔍 พบฟังก์ชันที่ถูกกำหนดซ้ำใน Blueprints:")
    for dup in duplicates:
        blueprint, endpoint, file_path = dup
        print(f"❌ Duplicate: {blueprint}.route('{endpoint}') ในไฟล์ {file_path}")
else:
    print("✅ ไม่มีฟังก์ชันซ้ำในโปรเจกต์นี้!")
