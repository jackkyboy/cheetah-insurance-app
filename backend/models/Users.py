# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Users.py
import logging
from backend.models import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Users(db.Model):
    """
    Represents a User entity in the application, linked to a customer account.
    """
    __tablename__ = 'Users'

    # Columns
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Primary key for Users table")
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False, comment="Foreign key referencing Customers")
    email = db.Column(db.String(255), unique=True, nullable=False, comment="User's email address (must be unique)")
    password_hash = db.Column(db.String(255), nullable=False, comment="Hashed password for secure authentication")
    profile_picture = db.Column(db.String(255), nullable=True, comment="Path to user's profile picture (if any)")
    bio = db.Column(db.Text, nullable=True, comment="Short biography or description of the user")
    theme_color = db.Column(db.String(7), nullable=True, comment="Hexadecimal code for user's profile theme color")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="Timestamp for when the user was created")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Timestamp for last profile update")

    # ✅ เพิ่ม role ลงใน Model Users (ถูกต้อง)
    role = db.Column(db.String(50), nullable=True, comment="User role (e.g. admin, user)")

    # Relationships
    customer = db.relationship('Customers', back_populates='user', lazy='joined')
    insurance_preparations = db.relationship('InsurancePreparation', back_populates='user', cascade='all, delete-orphan', lazy='select')


    def set_password(self, password):
        """
        Hashes the provided password and stores it in the password_hash field.
        """
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"Hashing password for user_id={self.user_id}")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies the provided password against the stored hash.
        """
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"Checking password for user_id={self.user_id}")
        return check_password_hash(self.password_hash, password)

    def update_profile(self, **kwargs):
        """
        Updates the user's profile details dynamically based on provided keyword arguments.

        Args:
            **kwargs: Key-value pairs of fields to update.

        Raises:
            ValueError: If any update operation fails.
        """
        logger.debug(f"Updating profile for user_id={self.user_id} with {kwargs}")
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            db.session.commit()
            logger.info(f"Profile updated successfully for user_id={self.user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating profile for user_id={self.user_id}: {e}")
            raise ValueError("Failed to update profile")

    def to_dict(self):
        """
        Converts the User object into a dictionary for JSON serialization.
        """
        logger.debug(f"Converting user_id={self.user_id} to dictionary")
        return {
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "theme_color": self.theme_color,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

    @staticmethod
    def get_user_by_id(user_id):
        """
        Retrieves a user by their user ID.

        Args:
            user_id (int): The user ID to search for.

        Returns:
            Users: The user object if found, or None if not found.
        """
        logger.debug(f"Fetching user by user_id: {user_id}")
        return Users.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        """
        Retrieves a user by their email address.
        """
        logger.debug(f"Fetching user by email: {email}")
        if not email:
            raise ValueError("Email cannot be empty")
        return Users.query.filter_by(email=email).first()

    @staticmethod
    def delete_user_by_id(user_id):
        """
        Deletes a user by their user_id.
        """
        logger.info(f"Deleting user_id={user_id}")
        user = Users.query.get(user_id)
        if not user:
            logger.warning(f"User not found with user_id={user_id}")
            raise ValueError("User not found")
        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User deleted successfully: user_id={user_id}")
            return {"message": "User deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user_id={user_id}: {e}")
            raise ValueError("Failed to delete user")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Changes the password for the user after verifying the old password.

        Args:
            user_id (int): The ID of the user changing their password.
            old_password (str): The current password.
            new_password (str): The new password to be set.

        Returns:
            dict: A success message upon successful password change.

        Raises:
            ValueError: If the old password does not match or if the new password is invalid.
        """
        logger.debug(f"Changing password for user_id={user_id}")
        user = Users.query.get(user_id)
        if not user:
            logger.error(f"User not found with user_id={user_id}")
            raise ValueError("User not found")

        if not user.check_password(old_password):
            logger.error(f"Old password does not match for user_id={user_id}")
            raise ValueError("Old password does not match")

        user.set_password(new_password)
        try:
            db.session.commit()
            logger.info(f"Password changed successfully for user_id={user_id}")
            return {"message": "Password changed successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error changing password for user_id={user_id}: {e}")
            raise ValueError("Failed to change password")
