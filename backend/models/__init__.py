# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/__init__.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/__init__.py
# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/__init__.py
import importlib
import logging
from backend.db import db  # ✅ ใช้ db instance เดียวจาก backend/db.py

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def initialize_models():
    """
    Dynamically import all models inside the models directory.
    This function ensures all models are properly loaded before migrations.
    """
    models = [
        "Admins",
        "CarInfo",
        "CarInsurancePackages",
        "ClaimIssues",
        "Claims",
        "Coupons",
        "CustomerInfo",
        "CustomerPolicies",
        "Customers",
        "Documents",
        "InsuranceCompanies",
        "InsuranceDataCenter",
        "InsurancePreparation",
        "InsuranceReviews",
        "Payments",
        "PolicyRequests",
        "Users"
    ]

    for model in models:
        try:
            importlib.import_module(f"backend.models.{model}")
            logger.debug(f"✅ Successfully imported model: {model}")
        except ImportError as e:
            logger.error(f"❌ Failed to import model {model}: {e}")


def init_app(app):
    """Initialize SQLAlchemy with the Flask app."""
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
        logger.debug("✅ SQLAlchemy initialized with Flask App")
    else:
        logger.debug("⚠️ SQLAlchemy already initialized with Flask App")

    with app.app_context():
        try:
            db.create_all()
            logger.debug("✅ Database tables created successfully.")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")


class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            logger.debug(f"✅ Saved {self.__class__.__name__}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Save error on {self.__class__.__name__}: {e}")

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            logger.debug(f"✅ Deleted {self.__class__.__name__}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Delete error on {self.__class__.__name__}: {e}")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
