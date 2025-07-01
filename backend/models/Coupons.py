from backend.models import db  # นำเข้า `db` จาก `__init__.py`
from datetime import datetime

# โมเดล Coupons
class Coupons(db.Model):
    __tablename__ = 'Coupons'

    coupon_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # รหัสคูปอง ต้องไม่ซ้ำ
    discount_percentage = db.Column(db.Float, nullable=False)  # ส่วนลด (%)
    expiration_date = db.Column(db.DateTime, nullable=False)  # วันหมดอายุ
    is_active = db.Column(db.Boolean, default=True)  # สถานะ Active

    # ความสัมพันธ์กับ CustomerCoupons
    assigned_to = db.relationship('CustomerCoupons', back_populates='coupon', lazy=True)

    def to_dict(self):
        """
        แปลงข้อมูลคูปองเป็น dictionary
        """
        return {
            "coupon_id": self.coupon_id,
            "code": self.code,
            "discount_percentage": self.discount_percentage,
            "expiration_date": self.expiration_date.strftime('%Y-%m-%d %H:%M:%S'),
            "is_active": self.is_active
        }


# โมเดล CustomerCoupons
class CustomerCoupons(db.Model):
    __tablename__ = 'Customer_Coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False)  # FK ไปยัง Customers
    coupon_id = db.Column(db.Integer, db.ForeignKey('Coupons.coupon_id'), nullable=False)  # FK ไปยัง Coupons
    assigned_date = db.Column(db.DateTime, default=db.func.now())  # วันที่แจกคูปอง
    redeemed = db.Column(db.Boolean, default=False)  # ใช้แล้วหรือยัง

    # ความสัมพันธ์กับ Coupons
    coupon = db.relationship('Coupons', back_populates='assigned_to')

    def to_dict(self):
        """
        แปลงข้อมูล CustomerCoupon เป็น dictionary
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "coupon": self.coupon.to_dict(),
            "assigned_date": self.assigned_date.strftime('%Y-%m-%d %H:%M:%S'),
            "redeemed": self.redeemed
        }


# ฟังก์ชันสำหรับสร้างคูปอง
def create_coupon(code, discount_percentage, expiration_date):
    """
    สร้างคูปองใหม่
    """
    if Coupons.query.filter_by(code=code).first():
        raise ValueError("Coupon code already exists.")  # ตรวจสอบว่ารหัสคูปองซ้ำหรือไม่

    try:
        coupon = Coupons(
            code=code,
            discount_percentage=discount_percentage,
            expiration_date=expiration_date
        )
        db.session.add(coupon)
        db.session.commit()  # บันทึกข้อมูลลงฐานข้อมูล
        return coupon.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to create coupon: {str(e)}")


# ฟังก์ชันสำหรับแจกคูปองให้ลูกค้า
def assign_coupon_to_customer(customer_id, coupon_id):
    """
    แจกคูปองให้ลูกค้าตาม customer_id และ coupon_id
    """
    coupon = Coupons.query.get(coupon_id)
    if not coupon:
        raise ValueError("Coupon not found.")
    if not coupon.is_active or coupon.expiration_date < datetime.utcnow():
        raise ValueError("Coupon is inactive or has expired.")  # ตรวจสอบว่าคูปองหมดอายุหรือถูกปิดใช้งาน

    assignment = CustomerCoupons(
        customer_id=customer_id,
        coupon_id=coupon_id
    )
    try:
        db.session.add(assignment)
        db.session.commit()  # บันทึกการแจกคูปอง
        return assignment.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to assign coupon: {str(e)}")


# ฟังก์ชันสำหรับดึงข้อมูลคูปองของลูกค้า
def get_customer_coupons(customer_id):
    """
    ดึงคูปองที่ยังไม่ถูกใช้ของลูกค้า
    """
    from backend.models.Customers import Customers  # Import โมเดล Customers
    customer = Customers.query.get(customer_id)
    if not customer:
        raise ValueError("Customer not found.")

    coupons = CustomerCoupons.query.filter_by(customer_id=customer_id, redeemed=False).all()
    return [coupon.to_dict() for coupon in coupons]


# ฟังก์ชันสำหรับ Redeem คูปอง
def redeem_coupon(customer_id, coupon_id):
    """
    Redeem คูปองที่ลูกค้าถืออยู่
    """
    customer_coupon = CustomerCoupons.query.filter_by(customer_id=customer_id, coupon_id=coupon_id, redeemed=False).first()
    if not customer_coupon:
        raise ValueError("Coupon not found or already redeemed.")

    try:
        customer_coupon.redeemed = True
        db.session.commit()
        return customer_coupon.to_dict()
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to redeem coupon: {str(e)}")
