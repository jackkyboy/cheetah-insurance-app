# /Users/apichet/Downloads/cheetah-insurance-app/backend/wsgi.py

# backend/wsgi.py

from backend.app import create_app

# ✅ Application Factory Pattern: ไม่ต้องมี app อยู่ตรงๆใน backend.app
application = create_app()  # <-- ใช้ชื่อ 'application' ปลอดภัยกับบาง WSGI server

# ✅ ใช้ได้กับ Gunicorn: `gunicorn backend.wsgi:application`
# ✅ ใช้ได้กับ Python ตรง: `python backend/wsgi.py`
if __name__ == "__main__":
    # Local Dev Mode Only
    application.run(host="0.0.0.0", port=5000, debug=True)
