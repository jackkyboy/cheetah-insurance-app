# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Customers.py
from datetime import datetime
import logging
from backend.db import (
    db, Model, Column, Integer, String, Text, DateTime, ForeignKey, relationship
)

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Customers(Model):
    """
    Represents a Customer entity in the application.
    """
    __tablename__ = 'Customers'

    customer_id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key for the Customers table")
    first_name = Column(String(50), nullable=False, comment="Customer's first name")
    last_name = Column(String(50), nullable=False, comment="Customer's last name")
    email = Column(String(255), unique=True, nullable=False, comment="Customer's unique email address")
    phone_number = Column(String(20), nullable=True, comment="Customer's phone number")
    address = Column(Text, nullable=True, comment="Customer's physical address")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Timestamp when the customer was created")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Timestamp when the customer was last updated")

    # Foreign key to Users
    user_id = Column(Integer, ForeignKey('Users.user_id'), nullable=False, unique=True, comment="Foreign key to Users table (1:1 relationship)")

    # Relationships
    user = relationship('Users', back_populates='customer', uselist=False, lazy='joined')
    documents = relationship('Documents', back_populates='customer', cascade='all, delete-orphan', lazy='select')
    car_info = relationship('CarInfo', back_populates='customer', cascade='all, delete-orphan', lazy='select')
    policies = relationship('CustomerPolicies', back_populates='customer', cascade='all, delete-orphan', lazy='select')
    policy_requests = relationship('PolicyRequests', back_populates='customer', cascade='all, delete-orphan', lazy='select')

    def to_dict(self):
        logger.debug(f"Converting customer_id={self.customer_id} to dictionary.")
        try:
            return {
                'customer_id': self.customer_id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'email': self.email,
                'phone_number': self.phone_number,
                'address': self.address,
                'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
                'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
                'car_info': [car.to_dict() for car in self.car_info],
                'documents': [doc.to_dict() for doc in self.documents],
                'policies': [policy.to_dict() for policy in self.policies],
                'policy_requests': [req.to_dict() for req in self.policy_requests],
            }
        except Exception as e:
            logger.error(f"Error converting customer to dictionary: {e}")
            raise ValueError("Failed to serialize customer data")

    @staticmethod
    def find_by_email(email):
        logger.debug(f"Finding customer by email: {email}")
        try:
            return Customers.query.filter_by(email=email).first()
        except Exception as e:
            logger.exception(f"Error finding customer by email: {e}")
            raise Exception(f"Failed to find customer by email: {str(e)}")

    @staticmethod
    def update_customer(customer_id, **kwargs):
        logger.debug(f"Updating customer_id={customer_id} with {kwargs}")
        try:
            customer = Customers.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found")

            for key, value in kwargs.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)

            db.session.commit()
            logger.info(f"Customer updated successfully: customer_id={customer_id}")
            return customer.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error updating customer: {e}")
            raise Exception(f"Failed to update customer: {str(e)}")

    @staticmethod
    def delete_customer(customer_id):
        logger.debug(f"Deleting customer_id={customer_id}")
        try:
            customer = Customers.query.get(customer_id)
            if not customer:
                raise ValueError("Customer not found")

            db.session.delete(customer)
            db.session.commit()
            logger.info(f"Customer deleted successfully: customer_id={customer_id}")
            return {"message": "Customer deleted successfully"}
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error deleting customer: {e}")
            raise Exception(f"Failed to delete customer: {str(e)}")
