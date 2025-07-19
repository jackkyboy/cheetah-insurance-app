# /Users/apichet/Downloads/cheetah-insurance-app/backend/db.py

from backend.models import db  # ✅ ดึง SQLAlchemy instance จาก models/__init__.py มาใช้

# ✅ ทำให้สามารถ import แบบ from backend import db ได้
__all__ = ['db']
