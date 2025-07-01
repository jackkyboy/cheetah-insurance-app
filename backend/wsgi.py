# /Users/apichet/Downloads/cheetah-insurance-app/backend/wsgi.py

# /backend/wsgi.py

from backend.app import create_app

# ✅ สร้าง Flask app ด้วย factory pattern
app = create_app()

# ✅ รองรับการรันตรง (เช่น python backend/wsgi.py)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
