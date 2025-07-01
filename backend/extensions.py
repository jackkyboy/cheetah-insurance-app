# /Users/apichet/Downloads/cheetah-insurance-app/backend/extensions.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/extensions.py
from flask_caching import Cache

# ✅ ใช้แค่ instance นี้เท่านั้น ห้ามสร้างใหม่ที่อื่น
cache = Cache(config={"CACHE_TYPE": "SimpleCache"})

def init_extensions(app):
    """
    Initialize and register all extensions with the Flask app.
    """
    # ✅ แนบ cache เข้ากับ app
    cache.init_app(app)

    # ✅ ผูก cache instance เข้ากับ app.extensions แบบปลอดภัย
    if "cache" not in app.extensions:
        app.extensions["cache"] = {}

    # ✅ Bind ทั้ง string และ object ref (กัน KeyError)
    app.extensions["cache"]["default"] = cache
    app.extensions["cache"][cache] = cache
