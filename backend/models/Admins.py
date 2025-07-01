# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Admins.py
from backend.models import db  # ✅ ใช้ db จาก models/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Admins(db.Model):
    __tablename__ = 'Admins'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin', nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # ✅ เพิ่มฟิลด์ `name`
    name = db.Column(db.String(255), nullable=True)  # ทำให้สามารถเป็น `null` ได้

    def set_password(self, password):
        """
        Hash and store the password in the database.
        """
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"🔐 Setting password for admin_id={self.admin_id}")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verify if the provided password matches the stored hash.
        """
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"🔍 Checking password for admin_id={self.admin_id}")
        return check_password_hash(self.password_hash, password)

    def update_refresh_token(self, token):
        """
        Update the refresh token for the admin.
        """
        if not token:
            raise ValueError("Refresh token cannot be empty")

        logger.debug(f"🔄 Saving new refresh token for admin_id={self.admin_id}: {token}")
        self.refresh_token = token
        db.session.commit()
        logger.info(f"✅ Refresh token updated for admin_id={self.admin_id}")

    def to_dict(self):
        """
        Convert Admin object to a dictionary for JSON serialization.
        """
        logger.debug(f"📌 Converting admin_id={self.admin_id} to dictionary")
        return {
            "admin_id": self.admin_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "refresh_token": self.refresh_token,
        }


# Service Functions

def create_admin(email, password, role='admin'):
    """
    Create a new Admin.
    """
    if Admins.query.filter_by(email=email).first():
        logger.error(f"❌ Admin creation failed: Email {email} already exists.")
        raise ValueError("Admin email already exists.")

    try:
        new_admin = Admins(email=email, role=role)
        new_admin.set_password(password)

        # ✅ ตรวจสอบว่า `admin_id` ถูกสร้างแล้วก่อนเรียก generate_refresh_token
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
    """
    Authenticate an Admin using email and password.
    """
    admin = Admins.query.filter_by(email=email).first()
    if not admin:
        logger.warning(f"❌ Login failed: Admin {email} not found.")
        raise ValueError("Invalid email or password.")

    if not admin.check_password(password):
        logger.warning(f"❌ Login failed: Incorrect password for {email}.")
        raise ValueError("Invalid email or password.")

    # ✅ ตรวจสอบว่า admin_id มีค่าก่อนสร้าง Refresh Token
    if not admin.admin_id:
        logger.error(f"❌ Error: Admin ID is missing for {email}.")
        raise ValueError("Admin ID is missing.")

    from backend.utils.jwt_utils import generate_refresh_token
    new_refresh_token = generate_refresh_token(admin_id=admin.admin_id, email=admin.email)

    logger.debug(f"🔄 Generating new Refresh Token for {email}: {new_refresh_token}")

    admin.update_refresh_token(new_refresh_token)
    logger.debug(f"✅ Updated Refresh Token in database for {email}")

    logger.info(f"✅ Admin logged in: {email}")
    return {
        **admin.to_dict(),
        "refresh_token": new_refresh_token
    }


def get_all_admins():
    """
    Retrieve all Admins in the system.
    """
    try:
        admins = Admins.query.all()
        logger.info(f"📊 Retrieved {len(admins)} admins.")
        return [admin.to_dict() for admin in admins]
    except Exception as e:
        logger.exception("❌ Error fetching admins")
        raise Exception(f"Failed to fetch admins: {str(e)}")
