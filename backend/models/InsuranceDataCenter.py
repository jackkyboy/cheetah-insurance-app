# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/InsuranceDataCenter.py
from backend import db
from datetime import datetime
import logging

# Logging Configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InsuranceDataCenter(db.Model):
    __tablename__ = 'insurance_data_center'

    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="Primary key for insurance data center")

    # Data Fields
    car_brand = db.Column(db.String(100), nullable=False, comment="Brand of the car")
    insurance_type = db.Column(db.String(100), nullable=False, comment="Type of insurance")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment="Record creation timestamp")

    def __repr__(self):
        return f"<InsuranceDataCenter {self.car_brand} - {self.insurance_type}>"

    def to_dict(self):
        """
        Convert object to dictionary for JSON response.
        """
        return {
            "id": self.id,
            "car_brand": self.car_brand,
            "insurance_type": self.insurance_type,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def update_data(self, data):
        """
        Update insurance data dynamically.
        """
        logger.debug(f"🔄 Updating InsuranceDataCenter record ID={self.id}")
        allowed_fields = {"car_brand", "insurance_type"}

        for key, value in data.items():
            if key in allowed_fields and hasattr(self, key):
                setattr(self, key, value)

        db.session.commit()
        logger.info(f"✅ InsuranceDataCenter record updated successfully ID={self.id}")

    @staticmethod
    def get_all():
        """
        Retrieve all records from InsuranceDataCenter.
        """
        try:
            records = InsuranceDataCenter.query.all()
            logger.info(f"✅ Retrieved {len(records)} records from InsuranceDataCenter.")
            return [record.to_dict() for record in records]
        except Exception as e:
            logger.exception("❌ Error fetching InsuranceDataCenter records")
            raise Exception(f"Failed to fetch records: {str(e)}")
