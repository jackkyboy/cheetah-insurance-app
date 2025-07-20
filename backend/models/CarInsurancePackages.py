# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/CarInsurancePackages.py
import logging
from backend.db import (
    db, Model, Column, Integer, String, Float, ForeignKey, Index, relationship
)

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CarInsurancePackages(Model):
    __tablename__ = 'Car_Insurance_Packages'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('Insurance_Companies.company_id'), nullable=False)

    car_brand = Column(String(100), nullable=False)
    car_model = Column(String(100), nullable=False)
    car_model_year = Column(String(4), nullable=False)
    car_submodel = Column(String(255), nullable=False)

    premium = Column(Float, nullable=False)
    cmi_amount = Column(Float, nullable=True)
    liability_per_person = Column(Float, nullable=True)
    liability_per_event = Column(Float, nullable=True)
    liability_property = Column(Float, nullable=True)
    liability_deductible = Column(Float, nullable=True)
    own_damage = Column(Float, nullable=True)
    own_theft_fire_damage = Column(Float, nullable=True)
    coverage_driver_death = Column(Float, nullable=True)
    coverage_passenger_death = Column(Float, nullable=True)
    coverage_medical_expense = Column(Float, nullable=True)
    coverage_bail_bond = Column(Float, nullable=True)
    repair_type = Column(String(50), nullable=True)

    policies = relationship('CustomerPolicies', back_populates='insurance_package', lazy=True)

    __table_args__ = (
        Index('idx_car_brand', 'car_brand'),
        Index('idx_car_model', 'car_model'),
        Index('idx_car_model_year', 'car_model_year'),
        Index('idx_search', 'car_brand', 'car_model', 'car_model_year', 'car_submodel'),
    )

    def to_dict(self):
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
