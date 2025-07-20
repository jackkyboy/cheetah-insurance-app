# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Admins.py
from backend.db import (
    db, Model, Column, Integer, String, Text, DateTime
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Admins(Model):  # ✅ ใช้ Model แทน db.Model
    __tablename__ = 'Admins'

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='admin', nullable=False)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    name = Column(String(255), nullable=True)

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"🔐 Setting password for admin_id={self.admin_id}")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"🔍 Checking password for admin_id={self.admin_id}")
        return check_password_hash(self.password_hash, password)

    def update_refresh_token(self, token):
        if not token:
            raise ValueError("Refresh token cannot be empty")

        logger.debug(f"🔄 Saving new refresh token for admin_id={self.admin_id}: {token}")
        self.refresh_token = token
        db.session.commit()
        logger.info(f"✅ Refresh token updated for admin_id={self.admin_id}")

    def to_dict(self):
        logger.debug(f"📌 Converting admin_id={self.admin_id} to dictionary")
        return {
            "admin_id": self.admin_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "refresh_token": self.refresh_token,
        }


# === Service Functions ===

def create_admin(email, password, role='admin'):
    if Admins.query.filter_by(email=email).first():
        logger.error(f"❌ Admin creation failed: Email {email} already exists.")
        raise ValueError("Admin email already exists.")

    try:
        new_admin = Admins(email=email, role=role)
        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()

        from backend.utils.jwt_utils import generate_refresh_token
        new_refresh_token = generate_refresh_token(admin_id=new_admin.admin_id, email=email)

        new_admin.update_refresh_token(new_refresh_token)

        logger.info(f"✅ Admin created successfully: {email}")
        return new_admin.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("❌ Error while creating admin")
        raise Exception(f"Failed to create admin: {str(e)}")


def login_admin(email, password):
    admin = Admins.query.filter_by(email=email).first()
    if not admin:
        logger.warning(f"❌ Login failed: Admin {email} not found.")
        raise ValueError("Invalid email or password.")

    if not admin.check_password(password):
        logger.warning(f"❌ Login failed: Incorrect password for {email}.")
        raise ValueError("Invalid email or password.")

    if not admin.admin_id:
        logger.error(f"❌ Error: Admin ID is missing for {email}.")
        raise ValueError("Admin ID is missing.")

    from backend.utils.jwt_utils import generate_refresh_token
    new_refresh_token = generate_refresh_token(admin_id=admin.admin_id, email=admin.email)

    logger.debug(f"🔄 Generating new Refresh Token for {email}: {new_refresh_token}")
    admin.update_refresh_token(new_refresh_token)

    logger.info(f"✅ Admin logged in: {email}")
    return {
        **admin.to_dict(),
        "refresh_token": new_refresh_token
    }


def get_all_admins():
    try:
        admins = Admins.query.all()
        logger.info(f"📊 Retrieved {len(admins)} admins.")
        return [admin.to_dict() for admin in admins]
    except Exception as e:
        logger.exception("❌ Error fetching admins")
        raise Exception(f"Failed to fetch admins: {str(e)}")
