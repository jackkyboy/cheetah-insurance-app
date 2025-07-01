# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/__init__.py
import importlib
import logging
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

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
    # ✅ Ensure only one SQLAlchemy instance is initialized
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
        logger.debug("✅ SQLAlchemy initialized with Flask App")
    else:
        logger.debug("⚠️ SQLAlchemy already initialized with Flask App")

    # ✅ Ensure the app context is active when creating tables
    with app.app_context():
        try:
            db.create_all()
            logger.debug("✅ Database tables created successfully.")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")


class BaseModel(db.Model):
    """
    Base model for common fields and methods across all models.
    """
    __abstract__ = True  # This tells SQLAlchemy not to create a table for this model
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    def save(self):
        """Save instance to database"""
        try:
            db.session.add(self)
            db.session.commit()
            logger.debug(f"✅ Successfully saved {self.__class__.__name__} instance to database.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error saving {self.__class__.__name__}: {e}")

    def delete(self):
        """Delete instance from database"""
        try:
            db.session.delete(self)
            db.session.commit()
            logger.debug(f"✅ Successfully deleted {self.__class__.__name__} instance from database.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error deleting {self.__class__.__name__}: {e}")

    def to_dict(self):
        """Convert model to dictionary"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
