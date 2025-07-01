# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/user_service.py
import os
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import joinedload
from backend.models.Users import Users
from backend.models.Customers import Customers
from backend.models.CarInfo import CarInfo
from backend.models.Documents import Documents
from backend import db
from backend.utils.jwt_utils import generate_jwt, decode_jwt, generate_refresh_token
from backend.config.config import Config

# Logging setup
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Directory for profile picture uploads
UPLOAD_DIR = os.path.abspath("uploads/profile_pictures")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UserService:

    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user and return JWT tokens.
        """
        logger.debug(f"Authenticating user with email: {email}")
        try:
            user = Users.query.options(joinedload(Users.customer)).filter_by(email=email).first()
            if not user or not user.check_password(password):
                logger.warning("❌ Invalid email or password")
                raise ValueError("Invalid email or password")

            # Generate JWT tokens
            access_token = generate_jwt(
                {"user_id": user.user_id, "sub": str(user.user_id)},
                expires_in_minutes=15
            )
            refresh_token = generate_refresh_token(
                user_id=user.user_id,
                email=user.email
            )

            logger.info(f"✅ User {email} authenticated successfully.")
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(),
                "customer": user.customer.to_dict()
            }
        except ValueError as ve:
            logger.warning(f"⚠️ Authentication failed: {ve}")
            raise ValueError(str(ve))
        except Exception as e:
            logger.exception("❌ Error during authentication")
            raise Exception("An unexpected error occurred during authentication")

    @staticmethod
    def upload_profile_picture(user_id, file):
        """
        Upload profile picture for the user.
        """
        logger.debug(f"Uploading profile picture for user_id: {user_id}")
        try:
            user = Users.query.get(user_id)
            if not user:
                logger.warning(f"⚠️ User not found for user_id={user_id}")
                raise ValueError("User not found")

            # Validate file type
            if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
                logger.warning("❌ Unsupported file type")
                raise ValueError("Unsupported file type. Please upload a .jpg or .png file.")

            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            full_filename = f"{user_id}_{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_DIR, full_filename)

            # Save file
            file.save(file_path)

            # ✅ Save relative path to DB (no /api)
            relative_path = f"uploads/profile_pictures/{full_filename}"
            user.profile_picture = relative_path

            db.session.commit()

            # ✅ Construct full API path for response
            api_path = f"/api/{relative_path}"

            logger.info(f"✅ Profile picture uploaded for user_id={user_id}")
            return {
                "message": "Profile picture uploaded successfully",
                "profile_picture": api_path
            }

        except ValueError as ve:
            logger.warning(f"⚠️ {ve}")
            raise ValueError(str(ve))
        except Exception as e:
            logger.exception("❌ Error uploading profile picture")
            db.session.rollback()
            raise Exception("Error uploading profile picture")



    @staticmethod
    def get_profile_with_documents(user_id):
        """
        Fetch user profile with documents and car info.
        """
        logger.debug(f"Fetching profile for user_id: {user_id}")
        try:
            user = Users.query.options(
                joinedload(Users.customer).joinedload(Customers.car_info),
                joinedload(Users.customer).joinedload(Customers.documents)
            ).filter_by(user_id=user_id).first()

            if not user:
                logger.warning(f"⚠️ User not found for user_id={user_id}")
                raise ValueError("User not found")

            # Prepare the profile data
            profile = {
                "user": user.to_dict(),
                "customer": user.customer.to_dict(),
                "documents": [doc.to_dict() for doc in user.customer.documents or []],
                "car_info": [car.to_dict() for car in user.customer.car_info or []],
            }
            logger.info(f"✅ Profile fetched for user_id={user_id}")
            return profile
        except ValueError as ve:
            logger.warning(f"⚠️ Profile fetch failed: {ve}")
            raise ValueError(str(ve))
        except Exception as e:
            logger.exception("❌ Error fetching profile")
            raise Exception("Error fetching user profile")

    @staticmethod
    def update_user_profile(user_id, data):
        """
        Update user and customer profile information.
        """
        logger.debug(f"Updating profile for user_id={user_id} with data: {data}")
        try:
            user = Users.query.get(user_id)
            if not user:
                logger.warning(f"⚠️ User not found for user_id={user_id}")
                raise ValueError("User not found")

            customer = user.customer
            if not customer:
                logger.warning(f"⚠️ Customer not found for user_id={user_id}")
                raise ValueError("Customer not found")

            # Update user and customer fields
            logger.debug("Updating user and customer fields...")
            user.bio = data.get("bio", user.bio)
            user.theme_color = data.get("theme_color", user.theme_color)
            customer.first_name = data.get("first_name", customer.first_name)
            customer.last_name = data.get("last_name", customer.last_name)
            customer.phone_number = data.get("phone_number", customer.phone_number)
            customer.address = data.get("address", customer.address)

            # Update car info if provided
            car_info_data = data.get("car_info")
            if car_info_data:
                car_info = CarInfo.query.filter_by(customer_id=customer.customer_id).first()
                if car_info:
                    logger.debug(f"Updating CarInfo for customer_id={customer.customer_id}: {car_info_data}")
                    car_info.car_brand = car_info_data.get("car_brand", car_info.car_brand)
                    car_info.car_model = car_info_data.get("car_model", car_info.car_model)
                    car_info.car_year = car_info_data.get("car_year", car_info.car_year)
                    car_info.car_submodel = car_info_data.get("car_submodel", car_info.car_submodel)
                else:
                    logger.debug(f"Creating new CarInfo for customer_id={customer.customer_id}: {car_info_data}")
                    car_info = CarInfo(
                        customer_id=customer.customer_id,
                        car_brand=car_info_data.get("car_brand", "Unknown"),
                        car_model=car_info_data.get("car_model", "Unknown"),
                        car_year=car_info_data.get("car_year"),
                        car_submodel=car_info_data.get("car_submodel", "Unknown")
                    )
                    db.session.add(car_info)

            db.session.commit()
            logger.info(f"✅ Profile updated for user_id={user_id}")
            return UserService.get_profile_with_documents(user_id)
        except Exception as e:
            db.session.rollback()
            logger.exception("❌ Error updating profile")
            raise Exception("Error updating profile")
