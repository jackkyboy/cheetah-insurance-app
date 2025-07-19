# /Users/apichet/Downloads/cheetah-insurance-app/backend/extensions.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/extensions.py
from backend.db import db  # ✅ import db instance ที่ดึงจาก models/__init__.py

# ...

def init_extensions(app):
    """
    Initialize and register all extensions with the Flask app.
    """
    # ✅ แนบ cache เข้ากับ app
    cache.init_app(app)

    if "cache" not in app.extensions:
        app.extensions["cache"] = {}
    app.extensions["cache"]["default"] = cache
    app.extensions["cache"][cache] = cache

    # ✅ แนบ db เข้ากับ app
    db.init_app(app)

    if "db" not in app.extensions:
        app.extensions["db"] = {}
    app.extensions["db"]["default"] = db
    app.extensions["db"][db] = db
