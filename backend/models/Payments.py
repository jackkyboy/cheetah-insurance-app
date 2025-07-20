# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Payments.py
from backend.db import db, Model, Column, Integer, String, Float, Text, Date, Time, DateTime, ForeignKey, relationship, func
import logging
import uuid
import urllib.parse

logger = logging.getLogger(__name__)


class Payments(Model):
    __tablename__ = 'Payments'

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(100), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False)
    package_id = Column(Integer, nullable=True)
    amount = Column(Float, nullable=False)
    premium = Column(Float, nullable=True)
    duty = Column(Float, nullable=True)
    vat = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    add_ons = Column(Text, nullable=True)
    coupon_code = Column(String(50), nullable=True)
    coverage_start_date = Column(Date, nullable=True)
    coverage_start_time = Column(Time, nullable=True)
    insurance_company = Column(String(255), nullable=True)
    insurance_type = Column(String(50), nullable=True)
    car_brand = Column(String(100), nullable=True)
    car_model = Column(String(100), nullable=True)
    car_submodel = Column(String(255), nullable=True)
    car_year = Column(Integer, nullable=True)
    payment_status = Column(String(50), default='pending')
    payment_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    customer = relationship('Customers', backref='payments', lazy=True)

    def to_dict(self):
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


# === Service Functions ===

def create_payment_order(customer_id, amount, currency='THB'):
    try:
        order_id = str(uuid.uuid4())
        logger.debug(f"Creating payment order for customer_id={customer_id}, amount={amount}, currency={currency}")
        payment = Payments(
            order_id=order_id,
            customer_id=customer_id,
            amount=amount,
            payment_status='pending'
        )
        payment.currency = currency  # Inject currency temporarily
        db.session.add(payment)
        db.session.commit()
        logger.info(f"Payment order created successfully: {order_id}")
        return payment.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error creating payment order.")
        raise Exception(f"Error creating payment order: {str(e)}")


def update_payment_status(order_id, status, payment_reference=None):
    try:
        logger.debug(f"Updating payment status for order_id={order_id} to status={status}")
        payment = Payments.query.filter_by(order_id=order_id).first()
        if not payment:
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
    try:
        logger.debug(f"Fetching payment order with order_id={order_id}")
        payment = Payments.query.filter_by(order_id=order_id).first()
        if not payment:
            raise ValueError("Order not found")
        return payment.to_dict()
    except Exception as e:
        logger.exception("Error fetching payment order.")
        raise Exception(f"Error fetching payment order: {str(e)}")


def generate_2c2p_payment_url(payment):
    try:
        base_url = "https://payment.2c2p.com/payment"
        params = {
            'order_id': payment.order_id,
            'amount': f"{payment.amount:.2f}",
            'currency': getattr(payment, 'currency', 'THB'),  # fallback currency
            'redirect_url': "https://your-website.com/payment/callback",
            'merchant_id': "YOUR_MERCHANT_ID"
        }
        query_string = urllib.parse.urlencode(params)
        return f"{base_url}?{query_string}"
    except Exception as e:
        logger.exception("Error generating 2C2P payment URL.")
        raise Exception(f"Error generating payment URL: {str(e)}")
