# /Users/apichet/Downloads/cheetah-insurance-app/backend/scripts/insert_admin.py
from backend import db, create_app
from backend.models.Admins import Admins
from werkzeug.security import generate_password_hash  # ✅ ใช้ของ werkzeug
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def insert_admin():
    try:
        email = "apichet.janya10@gmail.com"
        password = "Thehappiness@79"
        role = "admin"

        # 🔁 ลบ admin เดิมออกก่อนถ้ามี
        existing_admin = Admins.query.filter_by(email=email).first()
        if existing_admin:
            logger.warning(f"⚠️ Deleting existing admin: {email}")
            db.session.delete(existing_admin)
            db.session.commit()

        # ✅ แฮชด้วย werkzeug เพื่อให้ตรวจสอบตอน login ได้
        hashed_password = generate_password_hash(password, method="scrypt")  # หรือ method="pbkdf2:sha256"
        logger.debug(f"🔐 New Hashed Password: {hashed_password}")

        new_admin = Admins(email=email, role=role, password_hash=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        logger.info(f"✅ Admin created successfully: {email}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error creating admin: {e}")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        insert_admin()
