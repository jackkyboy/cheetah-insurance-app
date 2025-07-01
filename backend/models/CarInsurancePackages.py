# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CarInsurancePackages.py
import logging
from backend.models import db

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CarInsurancePackages(db.Model):
    __tablename__ = 'Car_Insurance_Packages'

    package_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('Insurance_Companies.company_id'), nullable=False)
    car_brand = db.Column(db.String(100), nullable=False)  # เพิ่มยี่ห้อรถยนต์
    car_model = db.Column(db.String(100), nullable=False)  # เพิ่มรุ่นรถยนต์
    car_model_year = db.Column(db.String(4), nullable=False)  # เพิ่มปีของรุ่นรถยนต์
    car_submodel = db.Column(db.String(255), nullable=False)
    premium = db.Column(db.Float, nullable=False)
    cmi_amount = db.Column(db.Float, nullable=True)
    liability_per_person = db.Column(db.Float, nullable=True)
    liability_per_event = db.Column(db.Float, nullable=True)
    liability_property = db.Column(db.Float, nullable=True)
    liability_deductible = db.Column(db.Float, nullable=True)
    own_damage = db.Column(db.Float, nullable=True)
    own_theft_fire_damage = db.Column(db.Float, nullable=True)
    coverage_driver_death = db.Column(db.Float, nullable=True)
    coverage_passenger_death = db.Column(db.Float, nullable=True)
    coverage_medical_expense = db.Column(db.Float, nullable=True)
    coverage_bail_bond = db.Column(db.Float, nullable=True)
    repair_type = db.Column(db.String(50), nullable=True)

    # ความสัมพันธ์กับ CustomerPolicies
    policies = db.relationship('CustomerPolicies', back_populates='insurance_package', lazy=True)

    # ดัชนีสำหรับเพิ่มประสิทธิภาพการค้นหา
    __table_args__ = (
        db.Index('idx_car_brand', 'car_brand'),
        db.Index('idx_car_model', 'car_model'),
        db.Index('idx_car_model_year', 'car_model_year'),
        db.Index('idx_search', 'car_brand', 'car_model', 'car_model_year', 'car_submodel'),
    )

    def to_dict(self):
        """
        แปลงข้อมูล CarInsurancePackage ให้อยู่ในรูปแบบ dictionary
        """
        try:
            logger.debug(f"Converting package_id={self.package_id} to dictionary.")
            return {
                'package_id': self.package_id,
                'company_id': self.company_id,
                'car_brand': self.car_brand,
                'car_model': self.car_model,
                'car_model_year': self.car_model_year,
                'car_submodel': self.car_submodel,
                'premium': self.premium,
                'cmi_amount': self.cmi_amount,
                'liability_per_person': self.liability_per_person,
                'liability_per_event': self.liability_per_event,
                'liability_property': self.liability_property,
                'liability_deductible': self.liability_deductible,
                'own_damage': self.own_damage,
                'own_theft_fire_damage': self.own_theft_fire_damage,
                'coverage_driver_death': self.coverage_driver_death,
                'coverage_passenger_death': self.coverage_passenger_death,
                'coverage_medical_expense': self.coverage_medical_expense,
                'coverage_bail_bond': self.coverage_bail_bond,
                'repair_type': self.repair_type,
            }
        except Exception as e:
            logger.error(f"Error converting CarInsurancePackages to dictionary: {e}")
            raise ValueError("Failed to serialize CarInsurancePackages data")

# Service Functions
def search_packages(car_brand, car_model, car_model_year, car_submodel=None):
    """
    ค้นหาแพ็กเกจประกันรถยนต์ตามเงื่อนไข
    """
    try:
        logger.debug(f"Searching packages for {car_brand} {car_model} {car_model_year} {car_submodel or ''}")
        query = CarInsurancePackages.query.filter_by(
            car_brand=car_brand,
            car_model=car_model,
            car_model_year=car_model_year
        )
        if car_submodel:
            query = query.filter_by(car_submodel=car_submodel)

        packages = query.all()
        logger.info(f"Found {len(packages)} packages.")
        return [package.to_dict() for package in packages]
    except Exception as e:
        logger.exception("Error searching car insurance packages.")
        raise Exception(f"Error searching car insurance packages: {e}")
