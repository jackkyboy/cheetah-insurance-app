# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/admin_service.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/admin_service.py
from backend.models import db
from backend.models.Admins import Admins
from backend.models.Users import Users
from backend.models.Customers import Customers
from backend.models.Payments import Payments
from backend.models.CustomerPolicies import CustomerPolicies
from backend.utils.password_utils import verify_scrypt_password, hash_password
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from backend.config.config import Config
import logging
import jwt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AdminService:

    @staticmethod
    def get_admin_by_id(admin_id):
        if not admin_id:
            logger.warning("⚠️ Invalid admin_id: None")
            return None
        return Admins.query.filter_by(admin_id=admin_id).first()

    @staticmethod
    def create_admin(email, password, role="admin", created_by=None):
        try:
            existing = Admins.query.filter_by(email=email).first()
            if existing:
                raise ValueError("Admin already exists.")

            hashed_pw = hash_password(password)
            admin = Admins(email=email, role=role, password_hash=hashed_pw, created_by=created_by)
            db.session.add(admin)
            db.session.commit()
            logger.info(f"✅ Admin created: {email}")
            return {
                "admin_id": admin.admin_id,
                "email": admin.email,
                "role": admin.role
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to create admin: {e}")
            raise e

    @staticmethod
    def delete_admin(admin_id):
        try:
            admin = Admins.query.get(admin_id)
            if not admin:
                return {"error": "Admin not found"}

            db.session.delete(admin)
            db.session.commit()
            return {"message": "Admin deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to delete admin: {e}")
            raise e

    @staticmethod
    def get_pending_users():
        try:
            pending_users = Users.query.filter_by(is_approved=False).all()
            return [
                {"user_id": u.user_id, "email": u.email, "name": u.name}
                for u in pending_users
            ]
        except Exception as e:
            logger.error(f"❌ Error getting pending users: {e}")
            raise e

    @staticmethod
    def approve_user(user_id, approved_by=None):
        try:
            user = Users.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            user.is_approved = True
            user.approved_by = approved_by
            user.approved_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"✅ User approved: {user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to approve user: {e}")
            raise e

    @staticmethod
    def reject_user(user_id, rejected_by=None):
        try:
            user = Users.query.get(user_id)
            if not user:
                raise ValueError("User not found")

            db.session.delete(user)
            db.session.commit()
            logger.info(f"❌ User rejected and deleted: {user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to reject user: {e}")
            raise e
        

    @staticmethod
    def login_admin(email, password):
        admin = Admins.query.filter_by(email=email).first()
        if not admin or not verify_scrypt_password(admin.password_hash, password):
            logger.warning(f"❌ Invalid credentials for: {email}")
            raise ValueError("Invalid email or password")

        access_payload = {
            "admin_id": admin.admin_id,
            "email": admin.email,
            "role": "admin",
            "exp": datetime.utcnow() + timedelta(hours=Config.ACCESS_TOKEN_EXPIRY_HOURS),
            "iat": datetime.utcnow(),
            "nbf": datetime.utcnow()
        }
        refresh_payload = {
            "admin_id": admin.admin_id,
            "exp": datetime.utcnow() + timedelta(days=Config.REFRESH_TOKEN_EXPIRY_DAYS)
        }

        return {
            "message": "Login successful",
            "access_token": jwt.encode(access_payload, Config.JWT_SECRET_KEY, algorithm="HS256"),
            "refresh_token": jwt.encode(refresh_payload, Config.JWT_SECRET_KEY, algorithm="HS256"),
            "admin": {
                "admin_id": admin.admin_id,
                "email": admin.email,
                "role": "admin"
            }
        }



    @staticmethod
    def get_all_admins():
        try:
            admins = Admins.query.all()
            return [
                {
                    "admin_id": a.admin_id,
                    "email": a.email,
                    "role": a.role,
                    "created_at": a.created_at.isoformat() if a.created_at else None
                }
                for a in admins
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get all admins: {e}")
            raise e

    @staticmethod
    def get_dashboard_stats():
        try:
            total_customers = Customers.query.count()
            total_policies = CustomerPolicies.query.count()
            total_payments = Payments.query.count()

            total_revenue = db.session.query(
                db.func.sum(Payments.total_price)
            ).filter(Payments.payment_status == "completed").scalar() or 0

            insurance_distribution = db.session.query(
                Payments.insurance_type,
                db.func.count(Payments.payment_id)
            ).group_by(Payments.insurance_type).all()

            monthly_sales = db.session.query(
                db.func.strftime('%Y-%m', Payments.created_at),
                db.func.sum(Payments.total_price)
            ).group_by(db.func.strftime('%Y-%m', Payments.created_at)).all()

            return {
                "total_customers": total_customers,
                "total_policies": total_policies,
                "total_payments": total_payments,
                "totalRevenue": total_revenue,
                "insuranceDistribution": {
                    "labels": [x[0] for x in insurance_distribution],
                    "data": [x[1] for x in insurance_distribution]
                },
                "monthlySales": {
                    "labels": [x[0] for x in monthly_sales],
                    "data": [x[1] for x in monthly_sales]
                }
            }
        except SQLAlchemyError as e:
            logger.error(f"❌ DB error: {e}")
            return {"error": "Database error fetching dashboard statistics."}
        except Exception as e:
            logger.error(f"❌ Error fetching stats: {e}")
            return {"error": "Unexpected server error."}
