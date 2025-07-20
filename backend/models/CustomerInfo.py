# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CustomerInfo.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CustomerInfo.py
import logging
from datetime import datetime
from backend.db import (
    db, Model, Column, Integer, String, DateTime, ForeignKey, relationship, backref
)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CustomerInfo(Model):
    """
    Represents additional customer-related information.
    """
    __tablename__ = 'Customer_Info'

    info_id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key for Customer_Info table")
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False, comment="Foreign key to Customers table")
    id_card_number = Column(String(20), nullable=True, comment="Customer's ID card number")
    driver_license_number = Column(String(20), nullable=True, comment="Customer's driver's license number")
    vehicle_registration = Column(String(50), nullable=True, comment="Customer's vehicle registration")
    policy_number = Column(String(50), nullable=True, comment="Customer's previous policy number")
    extracted_from = Column(String(50), nullable=False, comment="Source of data extraction (e.g., OCR, manual input)")
    created_at = Column(DateTime, default=db.func.now(), comment="Record creation timestamp")
    updated_at = Column(DateTime, onupdate=db.func.now(), comment="Record update timestamp")

    customer = relationship(
        'Customers',
        backref=backref('customer_info', lazy='select', cascade='all, delete-orphan')
    )

    def to_dict(self):
        logger.debug(f"Converting CustomerInfo ID {self.info_id} to dictionary.")
        return {
            "info_id": self.info_id,
            "customer_id": self.customer_id,
            "id_card_number": self.id_card_number,
            "driver_license_number": self.driver_license_number,
            "vehicle_registration": self.vehicle_registration,
            "policy_number": self.policy_number,
            "extracted_from": self.extracted_from,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "updated_at": self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }


# -------- Service Functions --------

def add_customer_info(customer_id, **kwargs):
    try:
        logger.debug(f"Adding customer info for customer_id={customer_id}")
        new_info = CustomerInfo(customer_id=customer_id, **kwargs)
        db.session.add(new_info)
        db.session.commit()
        logger.info(f"Customer info added successfully with ID {new_info.info_id}")
        return new_info.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error adding customer information.")
        raise Exception(f"Error adding customer information: {str(e)}")


def get_customer_info(customer_id):
    try:
        logger.debug(f"Fetching customer info for customer_id={customer_id}")
        info = CustomerInfo.query.filter_by(customer_id=customer_id).first()
        if not info:
            logger.warning(f"No customer info found for customer_id={customer_id}")
            return None
        logger.info(f"Customer info retrieved for customer_id={customer_id}")
        return info.to_dict()
    except Exception as e:
        logger.exception("Error fetching customer information.")
        raise Exception(f"Error fetching customer information: {str(e)}")


def get_all_customer_info():
    try:
        logger.debug("Fetching all customer info records.")
        info_list = CustomerInfo.query.all()
        logger.info(f"Retrieved {len(info_list)} customer info records.")
        return [info.to_dict() for info in info_list]
    except Exception as e:
        logger.exception("Error fetching all customer information.")
        raise Exception(f"Error fetching all customer information: {str(e)}")


def update_customer_info(info_id, **kwargs):
    try:
        logger.debug(f"Updating customer info with ID {info_id}")
        info = CustomerInfo.query.get(info_id)
        if not info:
            logger.warning(f"Customer info not found with ID {info_id}")
            raise ValueError("Customer info not found")

        for key, value in kwargs.items():
            if hasattr(info, key) and value is not None:
                setattr(info, key, value)

        db.session.commit()
        logger.info(f"Customer info updated successfully with ID {info_id}")
        return info.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error updating customer information.")
        raise Exception(f"Error updating customer information: {str(e)}")


def delete_customer_info(info_id):
    try:
        logger.debug(f"Deleting customer info with ID {info_id}")
        info = CustomerInfo.query.get(info_id)
        if not info:
            logger.warning(f"Customer info not found with ID {info_id}")
            raise ValueError("Customer info not found")

        db.session.delete(info)
        db.session.commit()
        logger.info(f"Customer info deleted successfully with ID {info_id}")
        return {"message": "Customer info deleted successfully"}
    except Exception as e:
        db.session.rollback()
        logger.exception("Error deleting customer information.")
        raise Exception(f"Error deleting customer information: {str(e)}")
