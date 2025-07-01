# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Payments.py
from backend.models import db
import logging
import uuid
from datetime import datetime
import urllib.parse

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Payments(db.Model):
    """
    Represents a payment order in the system.
    """
    __tablename__ = 'Payments'

    # Columns
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Primary key for Payments table")
    order_id = db.Column(db.String(100), unique=True, nullable=False, comment="Unique order ID generated for payment")
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False, comment="Foreign key to Customers table")
    package_id = db.Column(db.Integer, nullable=True, comment="Foreign key to selected insurance package (nullable for custom payments)")
    amount = db.Column(db.Float, nullable=False, comment="Total payment amount")  # Add this column
    premium = db.Column(db.Float, nullable=True, comment="Base insurance premium amount")
    duty = db.Column(db.Float, nullable=True, comment="Stamp duty")
    vat = db.Column(db.Float, nullable=True, comment="VAT (7%)")
    total_price = db.Column(db.Float, nullable=True, comment="Final total price including VAT, duty, and add-ons")
    add_ons = db.Column(db.Text, nullable=True, comment="Selected add-ons as comma-separated IDs")
    coupon_code = db.Column(db.String(50), nullable=True, comment="Coupon code applied")
    coverage_start_date = db.Column(db.Date, nullable=True, comment="Coverage start date")
    coverage_start_time = db.Column(db.Time, nullable=True, comment="Coverage start time")
    insurance_company = db.Column(db.String(255), nullable=True, comment="Selected insurance company name")
    insurance_type = db.Column(db.String(50), nullable=True, comment="Insurance type (e.g., ชั้น 1, ชั้น 2+)")
    car_brand = db.Column(db.String(100), nullable=True, comment="Car brand")
    car_model = db.Column(db.String(100), nullable=True, comment="Car model")
    car_submodel = db.Column(db.String(255), nullable=True, comment="Car submodel")
    car_year = db.Column(db.Integer, nullable=True, comment="Car year")
    payment_status = db.Column(db.String(50), default='pending', comment="Payment status: pending, success, failed")
    payment_reference = db.Column(db.String(255), nullable=True, comment="Reference ID from payment gateway")
    created_at = db.Column(db.DateTime, default=db.func.now(), comment="Timestamp when the payment was created")
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now(), comment="Timestamp when the payment was last updated")

    # Relationships
    customer = db.relationship('Customers', backref='payments', lazy=True)

    def to_dict(self):
        """
        Converts the Payments object into a dictionary for serialization.
        """
        logger.debug(f"Converting Payment ID {self.payment_id} to dictionary.")
        return {
            "payment_id": self.payment_id,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "package_id": self.package_id,
            "premium": self.premium,
            "duty": self.duty,
            "vat": self.vat,
            "total_price": self.total_price,
            "add_ons": self.add_ons,
            "coupon_code": self.coupon_code,
            "coverage_start_date": self.coverage_start_date.isoformat() if self.coverage_start_date else None,
            "coverage_start_time": self.coverage_start_time.isoformat() if self.coverage_start_time else None,
            "insurance_company": self.insurance_company,
            "insurance_type": self.insurance_type,
            "car_brand": self.car_brand,
            "car_model": self.car_model,
            "car_submodel": self.car_submodel,
            "car_year": self.car_year,
            "payment_status": self.payment_status,
            "payment_reference": self.payment_reference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Service Functions

def create_payment_order(customer_id, amount, currency='THB'):
    """
    Creates a new payment order.

    Args:
        customer_id (int): ID of the customer.
        amount (float): Amount to be paid.
        currency (str, optional): Currency of the payment. Defaults to 'THB'.

    Returns:
        dict: A dictionary representation of the created payment.
    """
    try:
        order_id = str(uuid.uuid4())  # Generate a unique order ID
        logger.debug(f"Creating payment order for customer_id={customer_id}, amount={amount}, currency={currency}")
        payment = Payments(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            payment_status='pending'
        )
        db.session.add(payment)
        db.session.commit()
        logger.info(f"Payment order created successfully: {order_id}")
        return payment.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error creating payment order.")
        raise Exception(f"Error creating payment order: {str(e)}")


def update_payment_status(order_id, status, payment_reference=None):
    """
    Updates the status of a payment order.

    Args:
        order_id (str): The unique order ID of the payment.
        status (str): The new status of the payment.
        payment_reference (str, optional): The payment gateway reference ID.

    Returns:
        dict: The updated payment details.
    """
    try:
        logger.debug(f"Updating payment status for order_id={order_id} to status={status}")
        payment = Payments.query.filter_by(order_id=order_id).first()
        if not payment:
            logger.warning(f"Payment order not found: {order_id}")
            raise ValueError("Order not found")

        payment.payment_status = status
        if payment_reference:
            payment.payment_reference = payment_reference

        db.session.commit()
        logger.info(f"Payment status updated successfully for order_id={order_id}")
        return payment.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error updating payment status.")
        raise Exception(f"Error updating payment status: {str(e)}")


def get_payment_order(order_id):
    """
    Retrieves payment details by order ID.

    Args:
        order_id (str): The unique order ID of the payment.

    Returns:
        dict: The payment details.
    """
    try:
        logger.debug(f"Fetching payment order with order_id={order_id}")
        payment = Payments.query.filter_by(order_id=order_id).first()
        if not payment:
            logger.warning(f"Payment order not found: {order_id}")
            raise ValueError("Order not found")
        return payment.to_dict()
    except Exception as e:
        logger.exception("Error fetching payment order.")
        raise Exception(f"Error fetching payment order: {str(e)}")


def generate_2c2p_payment_url(payment):
    """
    Generates a redirect URL for 2C2P payment gateway.

    Args:
        payment (Payments): The payment object.

    Returns:
        str: The redirect URL to the payment gateway.
    """
    try:
        base_url = "https://payment.2c2p.com/payment"
        params = {
            'order_id': payment.order_id,
            'amount': f"{payment.amount:.2f}",
            'currency': payment.currency,
            'redirect_url': "https://your-website.com/payment/callback",  # Replace with actual redirect URL
            'merchant_id': "YOUR_MERCHANT_ID"  # Replace with your 2C2P merchant ID
        }
        query_string = urllib.parse.urlencode(params)
        payment_url = f"{base_url}?{query_string}"
        logger.info(f"Generated 2C2P payment URL: {payment_url}")
        return payment_url
    except Exception as e:
        logger.exception("Error generating 2C2P payment URL.")
        raise Exception(f"Error generating payment URL: {str(e)}")
