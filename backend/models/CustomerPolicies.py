# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CustomerPolicies.py
import logging
from datetime import datetime, timedelta
from backend.models import db

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomerPolicies(db.Model):
    __tablename__ = 'Customer_Policies'

    policy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('Car_Insurance_Packages.package_id'), nullable=False)
    request_date = db.Column(db.DateTime, default=db.func.now)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='active')
    policy_number = db.Column(db.String(100), nullable=True)
    insurance_company_response = db.Column(db.Text, nullable=True)

    # ความสัมพันธ์กับ Customers
    customer = db.relationship('Customers', back_populates='policies', lazy='joined')

    # ความสัมพันธ์กับ CarInsurancePackages
    insurance_package = db.relationship('CarInsurancePackages', back_populates='policies', lazy='joined')

    def to_dict(self):
        """
        แปลงข้อมูลกรมธรรม์ให้อยู่ในรูปแบบ dictionary
        """
        try:
            logger.debug(f"Converting policy_id={self.policy_id} to dictionary.")
            return {
                'policy_id': self.policy_id,
                'customer_id': self.customer_id,
                'package_id': self.package_id,
                'request_date': self.request_date.strftime('%Y-%m-%d %H:%M:%S') if self.request_date else None,
                'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
                'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
                'status': self.status,
                'policy_number': self.policy_number,
                'insurance_company_response': self.insurance_company_response
            }
        except Exception as e:
            logger.error(f"Error converting CustomerPolicies to dictionary: {e}")
            raise ValueError("Failed to serialize CustomerPolicies data")


# Service Functions
def get_expiring_policies(days_before=30):
    """
    ค้นหากรมธรรม์ที่กำลังจะหมดอายุในช่วงเวลาที่กำหนด
    """
    try:
        notification_date = datetime.utcnow() + timedelta(days=days_before)
        logger.debug(f"Fetching policies expiring before: {notification_date}")
        
        expiring_policies = CustomerPolicies.query.filter(
            CustomerPolicies.end_date <= notification_date,
            CustomerPolicies.status == 'active'
        ).all()

        results = []
        for policy in expiring_policies:
            if policy.customer and policy.customer.user:
                results.append({
                    'policy_id': policy.policy_id,
                    'customer_id': policy.customer_id,
                    'end_date': policy.end_date.strftime('%Y-%m-%d'),
                    'customer_name': f"{policy.customer.first_name} {policy.customer.last_name}",
                    'email': policy.customer.email
                })

        logger.info(f"Found {len(results)} expiring policies.")
        return results
    except Exception as e:
        logger.exception("Error fetching expiring policies")
        raise Exception(f"Error fetching expiring policies: {e}")


def send_expiry_notifications():
    """
    ส่งอีเมลแจ้งเตือนกรมธรรม์ที่ใกล้หมดอายุ
    """
    try:
        logger.info("Sending expiry notifications...")
        expiring_policies = get_expiring_policies()

        if not expiring_policies:
            logger.info("No policies are expiring soon.")
            return {"message": "No policies expiring soon"}

        for policy in expiring_policies:
            logger.debug(f"Sending notification for policy_id={policy['policy_id']} to {policy['email']}")
            # Add actual email sending logic here (e.g., SMTP or a service like SendGrid)
            print(f"Sending notification to {policy['email']} for policy {policy['policy_id']} "
                f"expiring on {policy['end_date']}")

        logger.info(f"{len(expiring_policies)} notifications sent.")
        return {"message": f"{len(expiring_policies)} notifications sent."}
    except Exception as e:
        logger.exception("Error sending expiry notifications")
        raise Exception(f"Error sending expiry notifications: {e}")
