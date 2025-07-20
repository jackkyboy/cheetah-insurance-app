# backend/models/InsurancePreparation.py
from backend.db import db, Model, Column, Integer, DateTime, JSON, ForeignKey, relationship
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InsurancePreparation(Model):
    __tablename__ = "insurance_preparations"

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    insured_info = Column(JSON, nullable=True)
    motor_info = Column(JSON, nullable=True)
    policy_info = Column(JSON, nullable=True)
    driver_info = Column(JSON, nullable=True)
    beneficiary_info = Column(JSON, nullable=True)
    coverage_info = Column(JSON, nullable=True)
    consent_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship(
        "Users",
        back_populates="insurance_preparations",
        lazy="joined"
    )

    def __init__(self, user_id, insured_info=None, motor_info=None, policy_info=None,
                 driver_info=None, beneficiary_info=None, coverage_info=None, consent_info=None):
        self.user_id = user_id
        self.insured_info = insured_info or {}
        self.motor_info = motor_info or {}
        self.policy_info = policy_info or {}
        self.driver_info = driver_info or {}
        self.beneficiary_info = beneficiary_info or {}
        self.coverage_info = coverage_info or {}
        self.consent_info = consent_info or {}

    def to_dict(self):
        logger.debug(f"Converting InsurancePreparation ID {self.id} to dictionary.")
        return {
            "id": self.id,
            "user_id": self.user_id,
            "insured_info": self.insured_info,
            "motor_info": self.motor_info,
            "policy_info": self.policy_info,
            "driver_info": self.driver_info,
            "beneficiary_info": self.beneficiary_info,
            "coverage_info": self.coverage_info,
            "consent_info": self.consent_info,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_email": self.user.email if self.user else None,
        }

    @staticmethod
    def get_preparations_by_user(user_id):
        logger.debug(f"Fetching insurance preparations for user_id={user_id}")
        try:
            preparations = InsurancePreparation.query.filter_by(user_id=user_id).all()
            logger.info(f"Found {len(preparations)} preparations for user_id={user_id}")
            return [prep.to_dict() for prep in preparations]
        except Exception as e:
            logger.exception(f"Error fetching preparations for user_id={user_id}")
            raise Exception(f"Error fetching preparations: {str(e)}")

    @staticmethod
    def delete_preparation(preparation_id):
        logger.debug(f"Deleting insurance preparation with ID {preparation_id}")
        try:
            preparation = InsurancePreparation.query.get(preparation_id)
            if not preparation:
                logger.warning(f"Preparation not found with ID {preparation_id}")
                raise ValueError("Preparation not found")

            db.session.delete(preparation)
            db.session.commit()
            logger.info(f"Insurance preparation deleted successfully with ID {preparation_id}")
            return {"message": "Insurance preparation deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error deleting preparation ID {preparation_id}")
            raise Exception(f"Error deleting preparation: {str(e)}")
