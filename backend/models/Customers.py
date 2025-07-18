# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Customers.py
from datetime import datetime, timedelta
from backend.models import db  # Import `db` from `__init__.py`
from backend.models.CustomerPolicies import CustomerPolicies
import logging

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Customers(db.Model):
    """
    Represents a Customer entity in the application.
    """
    __tablename__ = 'Customers'

    # Columns
    # Columns
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Primary key for the Customers table")
    first_name = db.Column(db.String(50), nullable=False, comment="Customer's first name")
    last_name = db.Column(db.String(50), nullable=False, comment="Customer's last name")
    email = db.Column(db.String(255), unique=True, nullable=False, comment="Customer's unique email address")
    phone_number = db.Column(db.String(20), nullable=True, comment="Customer's phone number")
    address = db.Column(db.Text, nullable=True, comment="Customer's physical address")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="Timestamp when the customer was created")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="Timestamp when the customer was last updated")

    # ✅ เพิ่ม ForeignKey → Users
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=False, unique=True, comment="Foreign key to Users table (1:1 relationship)")


    # Relationships
    user = db.relationship(
        'Users',
        back_populates='customer',
        uselist=False,
        lazy='joined'
    )
    documents = db.relationship(
        'Documents',
        back_populates='customer',
        cascade='all, delete-orphan',
        lazy='select'
    )
    car_info = db.relationship(
        'CarInfo',
        back_populates='customer',
        cascade='all, delete-orphan',
        lazy='select'
    )
    policies = db.relationship(
        'CustomerPolicies',
        back_populates='customer',
        cascade='all, delete-orphan',
        lazy='select'
    )
    policy_requests = db.relationship(
        'PolicyRequests',
        back_populates='customer',
        cascade='all, delete-orphan',
        lazy='select'
    )

    def to_dict(self):
        """
        Converts the Customer object to a dictionary for JSON serialization.
        """
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
        """
        Finds a customer by their email address.

        Args:
            email (str): The email address of the customer.

        Returns:
            Customers: The customer object if found, or None if not found.
        """
        logger.debug(f"Finding customer by email: {email}")
        try:
            return Customers.query.filter_by(email=email).first()
        except Exception as e:
            logger.exception(f"Error finding customer by email: {e}")
            raise Exception(f"Failed to find customer by email: {str(e)}")

    @staticmethod
    def update_customer(customer_id, **kwargs):
        """
        Updates customer information.

        Args:
            customer_id (int): The ID of the customer to update.
            **kwargs: Key-value pairs of fields to update.

        Returns:
            dict: The updated customer data.
        """
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
        """
        Deletes a customer by their ID.

        Args:
            customer_id (int): The ID of the customer to delete.

        Returns:
            dict: A success message upon successful deletion.
        """
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
