from werkzeug.security import check_password_hash

# แทนค่า hash ที่ได้จาก Table Admins
stored_password_hash = "scrypt:32768:8:1$lK2DNc9ZBScYk0vK$048b1a0e666752ffadabfd6cf67726c1d8ae657e74f5814a6b770fe381ac877bc260e3f52f7c074117dea4bb130ab54e96df5c6068f0b3ae149c98fe52efc68e"

# แทนด้วยรหัสผ่านที่ต้องการตรวจสอบ
input_password = "Thehappiness@79"

# ตรวจสอบรหัสผ่าน
if check_password_hash(stored_password_hash, input_password):
    print("✅ Password matches!")
else:
    print("❌ Password does not match!")
