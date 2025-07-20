# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Users.py
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from backend.db import (
    db, Model, Column, Integer, String, Text, DateTime, relationship
)

logger = logging.getLogger(__name__)


class Users(Model):
    """
    Represents a User entity in the application, linked to a customer account.
    """
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key for Users table")
    email = Column(String(255), unique=True, nullable=False, comment="User's email address (must be unique)")
    password_hash = Column(String(255), nullable=False, comment="Hashed password for secure authentication")
    profile_picture = Column(String(255), nullable=True, comment="Path to user's profile picture")
    bio = Column(Text, nullable=True, comment="Short biography or description of the user")
    theme_color = Column(String(7), nullable=True, comment="Hexadecimal code for profile theme color")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Created timestamp")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Last updated timestamp")
    role = Column(String(50), nullable=True, comment="User role (admin, user, etc.)")

    # Relationships
    customer = relationship('Customers', back_populates='user', uselist=False, lazy='joined')
    insurance_preparations = relationship('InsurancePreparation', back_populates='user', cascade='all, delete-orphan', lazy='select')

    def set_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"Hashing password for user_id={self.user_id}")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not password:
            raise ValueError("Password cannot be empty")
        logger.debug(f"Checking password for user_id={self.user_id}")
        return check_password_hash(self.password_hash, password)

    def update_profile(self, **kwargs):
        logger.debug(f"Updating profile for user_id={self.user_id} with {kwargs}")
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            logger.info(f"✅ Profile updated: user_id={self.user_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to update profile: {e}")
            raise ValueError("Failed to update profile")

    def to_dict(self):
        logger.debug(f"Converting user_id={self.user_id} to dict")
        return {
            "user_id": self.user_id,
            "customer_id": self.customer.customer_id if self.customer else None,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "bio": self.bio,
            "theme_color": self.theme_color,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }

    @staticmethod
    def get_user_by_id(user_id):
        logger.debug(f"Fetching user_id={user_id}")
        return Users.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        logger.debug(f"Fetching user by email: {email}")
        if not email:
            raise ValueError("Email cannot be empty")
        return Users.query.filter_by(email=email).first()

    @staticmethod
    def delete_user_by_id(user_id):
        logger.info(f"Deleting user_id={user_id}")
        user = Users.query.get(user_id)
        if not user:
            logger.warning(f"User not found with user_id={user_id}")
            raise ValueError("User not found")
        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"✅ User deleted: user_id={user_id}")
            return {"message": "User deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Delete failed: {e}")
            raise ValueError("Failed to delete user")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        logger.debug(f"Changing password for user_id={user_id}")
        user = Users.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        if not user.check_password(old_password):
            raise ValueError("Old password does not match")

        user.set_password(new_password)
        try:
            db.session.commit()
            logger.info(f"✅ Password changed for user_id={user_id}")
            return {"message": "Password changed successfully"}
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Failed to change password: {e}")
            raise ValueError("Failed to change password")
