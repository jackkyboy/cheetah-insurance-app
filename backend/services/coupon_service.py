from backend.models.Coupons import Coupons
from backend import db
from datetime import datetime

class CouponService:
    @staticmethod
    def validate_coupon_availability(coupon):
        """
        ตรวจสอบความพร้อมใช้งานของคูปอง
        """
        if not coupon or not coupon.is_active:
            raise ValueError("Coupon is not available or inactive.")
        if coupon.expiration_date < datetime.utcnow():
            raise ValueError("Coupon has already expired.")

    @staticmethod
    def assign_coupon_to_customer(customer_id, coupon_id):
        """
        มอบคูปองให้ลูกค้า
        """
        coupon = Coupons.query.get(coupon_id)
        CouponService.validate_coupon_availability(coupon)

        assignment = CustomerCoupons(customer_id=customer_id, coupon_id=coupon_id)
        db.session.add(assignment)
        db.session.commit()
        return {
            "customer_id": assignment.customer_id,
            "coupon_id": assignment.coupon_id,
            "assigned_date": assignment.assigned_date
        }

    @staticmethod
    def redeem_coupon(customer_id, coupon_id):
        """
        ใช้งานคูปอง
        """
        customer_coupon = CustomerCoupons.query.filter_by(customer_id=customer_id, coupon_id=coupon_id, redeemed=False).first()
        if not customer_coupon:
            raise ValueError("Coupon not found or already redeemed.")

        CouponService.validate_coupon_availability(customer_coupon.coupon)

        customer_coupon.redeemed = True
        db.session.commit()
        return {
            'message': 'Coupon redeemed successfully',
            'coupon_id': customer_coupon.coupon_id,
            'code': customer_coupon.coupon.code,
            'discount_percentage': customer_coupon.coupon.discount_percentage
        }
