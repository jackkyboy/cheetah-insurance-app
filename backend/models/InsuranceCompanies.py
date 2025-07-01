# backend/models/InsuranceCompanies.py
import logging
from datetime import datetime
from backend.models import db  # Import `db` from `__init__.py`

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class InsuranceCompanies(db.Model):
    __tablename__ = 'Insurance_Companies'

    # Primary Key
    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Company Details
    company_code = db.Column(db.String(50), nullable=False, unique=True, comment="Unique company code")
    company_name_th = db.Column(db.String(255), nullable=False, comment="Company name in Thai")
    company_name_en = db.Column(db.String(255), nullable=False, comment="Company name in English")
    company_symbol = db.Column(db.String(50), nullable=False, comment="Company symbol")
    company_address1 = db.Column(db.Text, nullable=False, comment="Company main address")
    company_postcode = db.Column(db.String(10), nullable=False, comment="Company postcode")
    company_tax_id = db.Column(db.String(50), nullable=False, unique=True, comment="Company Tax ID")
    company_tel = db.Column(db.String(50), nullable=False, comment="Company contact telephone")
    company_email = db.Column(db.String(255), nullable=False, comment="Company contact email")
    company_claim_contact = db.Column(db.String(50), nullable=False, comment="Company claim contact info")

    # API Credentials
    api_base_url = db.Column(db.String(255), nullable=False, comment="API Base URL")
    api_token = db.Column(db.String(255), nullable=True, comment="API Authentication Token")
    token_expiration = db.Column(db.DateTime, nullable=True, comment="Token Expiration Time")
    last_token_refresh = db.Column(db.DateTime, nullable=True, comment="Last Token Refresh Timestamp")
    agent_code = db.Column(db.String(50), nullable=False, comment="API Agent Code")
    partner_code = db.Column(db.String(50), nullable=False, comment="API Partner Code")

    # Relationships
    policy_requests = db.relationship('PolicyRequests', back_populates='company', lazy='joined', cascade="all, delete-orphan")

    def is_token_valid(self):
        """
        Check if the API token is still valid.
        """
        if not self.token_expiration:
            logger.debug(f"🔴 Token for company_id={self.company_id} is invalid (no expiration date).")
            return False
        is_valid = self.token_expiration > datetime.utcnow()
        logger.debug(f"🟢 Token validity for company_id={self.company_id}: {is_valid}")
        return is_valid

    def refresh_token(self, new_token, expiration):
        """
        Update the API token details.
        """
        logger.debug(f"🔄 Refreshing token for company_id={self.company_id}")
        self.api_token = new_token
        self.token_expiration = expiration
        self.last_token_refresh = datetime.utcnow()
        db.session.commit()
        logger.info(f"✅ Token refreshed successfully for company_id={self.company_id}")

    def update_company_info(self, data):
        """
        Update company details dynamically.
        """
        logger.debug(f"🔄 Updating company info for company_id={self.company_id}")
        allowed_fields = {
            "company_code", "company_name_th", "company_name_en", "company_symbol",
            "company_address1", "company_postcode", "company_tax_id", "company_tel",
            "company_email", "company_claim_contact", "api_base_url",
            "agent_code", "partner_code"
        }

        for key, value in data.items():
            if key in allowed_fields and hasattr(self, key):
                setattr(self, key, value)

        db.session.commit()
        logger.info(f"✅ Company details updated successfully for company_id={self.company_id}")

    def to_dict(self):
        """
        Convert company details to a dictionary format.
        """
        logger.debug(f"📄 Converting company_id={self.company_id} to dictionary.")
        return {
            "company_id": self.company_id,
            "company_code": self.company_code,
            "company_name_th": self.company_name_th,
            "company_name_en": self.company_name_en,
            "company_symbol": self.company_symbol,
            "company_address1": self.company_address1,
            "company_postcode": self.company_postcode,
            "company_tax_id": self.company_tax_id,
            "company_tel": self.company_tel,
            "company_email": self.company_email,
            "company_claim_contact": self.company_claim_contact,
            "api_base_url": self.api_base_url,
            "agent_code": self.agent_code,
            "partner_code": self.partner_code,
            "token_expiration": self.token_expiration.strftime('%Y-%m-%d %H:%M:%S') if self.token_expiration else None,
            "last_token_refresh": self.last_token_refresh.strftime('%Y-%m-%d %H:%M:%S') if self.last_token_refresh else None
        }
