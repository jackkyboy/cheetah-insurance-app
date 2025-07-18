# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/auth_services.py
import logging
import traceback
import datetime
from sqlalchemy.orm import joinedload
from werkzeug.security import generate_password_hash, check_password_hash

from backend.models.Users import Users
from backend.models.Customers import Customers
from backend.models import db
from backend.utils.jwt_utils import generate_jwt, decode_jwt, generate_refresh_token
from backend.config.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=Config.LOG_LEVEL)

class AuthService:
    @staticmethod
    def register_user(email, password, first_name, last_name):
        logger.info(f"🔄 Registering user: {email}")
        try:
            if not all([email, password, first_name, last_name]):
                raise ValueError("All fields are required.")

            if Users.query.filter_by(email=email).first():
                logger.warning(f"⚠️ Email already exists: {email}")
                raise ValueError("Email already registered.")

            # ✅ Create user first
            hashed_password = generate_password_hash(password)
            new_user = Users(email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.flush()  # ➜ get user_id

            # ✅ Then create customer tied to user
            new_customer = Customers(
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_id=new_user.user_id
            )
            db.session.add(new_customer)

            db.session.commit()
            logger.info(f"✅ User created: user_id={new_user.user_id}")
            return {
                "user_id": new_user.user_id,
                "customer_id": new_customer.customer_id,
                "email": new_user.email
            }

        except ValueError as ve:
            db.session.rollback()
            logger.warning(f"⚠️ Register failed: {str(ve)}")
            raise ve
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Exception during register: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")

    @staticmethod
    def login_user(email, password):
        logger.info(f"🔄 Logging in: {email}")
        try:
            user = Users.query.options(joinedload(Users.customer)).filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                logger.warning("⚠️ Invalid email or password")
                raise ValueError("Invalid email or password.")

            role = user.role if user.role else "user"

            access_token = generate_jwt({
                "user_id": user.user_id,
                "email": user.email,
                "role": role,
            }, expires_in_minutes=15)

            refresh_token = generate_refresh_token(
                user_id=user.user_id,
                email=user.email
            )

            logger.info(f"✅ Login success: user_id={user.user_id}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "customer_id": user.customer.customer_id if user.customer else None,  # ✅ ดึงจาก relationship
                    "role": role,
                },
            }

        except ValueError as ve:
            logger.warning(f"⚠️ Login failed: {str(ve)}")
            raise ValueError("Unauthorized: Invalid credentials")
        except Exception as e:
            logger.error(f"❌ Login exception: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")


    @staticmethod
    def refresh_token(refresh_token):
        logger.info("🔄 Refreshing access token")
        try:
            payload = decode_jwt(refresh_token)

            if int(payload["exp"]) < int(datetime.datetime.utcnow().timestamp()):
                logger.warning("⚠️ Refresh token expired")
                raise ValueError("Refresh token expired")

            new_access_token = generate_jwt({
                "user_id": payload["user_id"],
                "email": payload["email"],
                "role": payload.get("role", "user"),
            }, expires_in_minutes=15)

            logger.info(f"✅ Token refreshed for user_id={payload['user_id']}")
            return {"access_token": new_access_token}

        except ValueError as ve:
            logger.warning(f"⚠️ Refresh token invalid: {str(ve)}")
            raise ValueError("Invalid refresh token or expired.")
        except Exception as e:
            logger.error(f"❌ Refresh error: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")
