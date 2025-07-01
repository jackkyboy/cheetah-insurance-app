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
    def register_user(email, password, customer_id):
        logger.info(f"🔄 Attempting to register user with email: {email}")
        try:
            if not email or not password:
                raise ValueError("❌ Email and password are required.")

            if Users.query.filter_by(email=email).first():
                logger.warning(f"⚠️ Email already registered: {email}")
                raise ValueError("Email already registered.")

            customer = Customers.query.get(customer_id)
            if not customer:
                logger.error(f"❌ Customer not found for ID: {customer_id}")
                raise ValueError("Customer ID does not exist.")

            hashed_password = generate_password_hash(password)
            new_user = Users(email=email, password_hash=hashed_password, customer_id=customer_id)
            db.session.add(new_user)
            db.session.commit()

            logger.info(f"✅ User registered successfully: user_id={new_user.user_id}")
            return {"user_id": new_user.user_id, "email": new_user.email}

        except ValueError as ve:
            db.session.rollback()
            logger.warning(f"⚠️ Registration failed: {str(ve)}")
            raise ve
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error during user registration: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")

    @staticmethod
    def login_user(email, password):
        logger.info(f"🔄 Attempting to log in user with email: {email}")
        try:
            user = Users.query.options(joinedload(Users.customer)).filter_by(email=email).first()
            if not user:
                logger.warning(f"❌ Login failed: User not found ({email})")
                raise ValueError("Invalid email or password.")

            if not check_password_hash(user.password_hash, password):
                logger.warning(f"❌ Login failed: Incorrect password for {email}")
                raise ValueError("Invalid email or password.")

            role = user.role if user.role else "user"  # ✅ แก้ให้มีค่า default

            access_token = generate_jwt(
                {"user_id": user.user_id, "email": user.email, "role": role},
                expires_in_minutes=15
            )
            refresh_token = generate_refresh_token(
                user_id=user.user_id,
                email=user.email
            )

            logger.info(f"✅ User logged in successfully: user_id={user.user_id}")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "customer_id": user.customer_id,
                    "role": role,
                },
            }

        except ValueError as ve:
            logger.warning(f"⚠️ Login failed: {str(ve)}")
            raise ValueError("Unauthorized: Invalid credentials")
        except Exception as e:
            logger.error(f"❌ Error during login process: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")

    @staticmethod
    def refresh_token(refresh_token):
        logger.info("🔄 Attempting to refresh access token")
        try:
            payload = decode_jwt(refresh_token)

            if int(payload["exp"]) < int(datetime.datetime.utcnow().timestamp()):  # ✅ แก้ TypeError
                logger.warning("⚠️ Refresh token expired")
                raise ValueError("Refresh token expired")

            new_access_token = generate_jwt(
                {"user_id": payload["user_id"], "email": payload["email"], "role": payload.get("role", "user")},
                expires_in_minutes=15
            )

            logger.info(f"✅ Access token refreshed successfully for user_id={payload['user_id']}")
            return {"access_token": new_access_token}

        except ValueError as ve:
            logger.warning(f"⚠️ Refresh token failed: {str(ve)}")
            raise ValueError("Invalid refresh token or expired.")
        except Exception as e:
            logger.error(f"❌ Error during refresh token process: {str(e)}")
            logger.debug(traceback.format_exc())
            raise Exception("Internal server error")
