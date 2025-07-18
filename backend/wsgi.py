# /Users/apichet/Downloads/cheetah-insurance-app/backend/wsgi.py

# backend/wsgi.py

from backend.app import create_app

# ✅ สร้าง Flask app ด้วย Application Factory Pattern
app = create_app()

# ✅ ใช้ได้ทั้งรันด้วย Gunicorn (เช่น gunicorn backend.wsgi:app)
# ✅ หรือรันตรงสำหรับ dev (เช่น python backend/wsgi.py)
if __name__ == "__main__":
    # เหมาะสำหรับ local dev เท่านั้น
    app.run(host="0.0.0.0", port=5000, debug=True)
