from datetime import datetime
from backend.db import (
    db, Model, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, relationship
)


class Coupons(Model):
    __tablename__ = 'Coupons'

    coupon_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    assigned_to = relationship('CustomerCoupons', back_populates='coupon', lazy=True)

    def to_dict(self):
        return {
            "coupon_id": self.coupon_id,
            "code": self.code,
            "discount_percentage": self.discount_percentage,
            "expiration_date": self.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
            "is_active": self.is_active
        }


class CustomerCoupons(Model):
    __tablename__ = 'Customer_Coupons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False)
    coupon_id = Column(Integer, ForeignKey('Coupons.coupon_id'), nullable=False)
    assigned_date = Column(DateTime, default=db.func.now())
    redeemed = Column(Boolean, default=False)

    coupon = relationship('Coupons', back_populates='assigned_to')

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "coupon": self.coupon.to_dict(),
            "assigned_date": self.assigned_date.strftime('%Y-%m-%d %H:%M:%S'),
            "redeemed": self.redeemed
        }


# ----------- Service Functions -----------

def create_coupon(code, discount_percentage, expiration_date):
    if Coupons.query.filter_by(code=code).first():
        raise ValueError("Coupon code already exists.")

    try:
        coupon = Coupons(
            code=code,
            discount_percentage=discount_percentage,
            expiration_date=expiration_date
        )
        db.session.add(coupon)
        db.session.commit()
        return coupon.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to create coupon: {str(e)}")


def assign_coupon_to_customer(customer_id, coupon_id):
    coupon = Coupons.query.get(coupon_id)
    if not coupon:
        raise ValueError("Coupon not found.")
    if not coupon.is_active or coupon.expiration_date < datetime.utcnow():
        raise ValueError("Coupon is inactive or has expired.")

    assignment = CustomerCoupons(
        customer_id=customer_id,
        coupon_id=coupon_id
    )
    try:
        db.session.add(assignment)
        db.session.commit()
        return assignment.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to assign coupon: {str(e)}")


def get_customer_coupons(customer_id):
    from backend.models.Customers import Customers
    customer = Customers.query.get(customer_id)
    if not customer:
        raise ValueError("Customer not found.")

    coupons = CustomerCoupons.query.filter_by(customer_id=customer_id, redeemed=False).all()
    return [coupon.to_dict() for coupon in coupons]


def redeem_coupon(customer_id, coupon_id):
    customer_coupon = CustomerCoupons.query.filter_by(
        customer_id=customer_id,
        coupon_id=coupon_id,
        redeemed=False
    ).first()
    if not customer_coupon:
        raise ValueError("Coupon not found or already redeemed.")

    try:
        customer_coupon.redeemed = True
        db.session.commit()
        return customer_coupon.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to redeem coupon: {str(e)}")
