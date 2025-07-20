from datetime import datetime
import logging
import requests

from backend.db import db, Model, Column, Integer, String, Float, Text, DateTime, ForeignKey, relationship, func
from backend.models.InsuranceCompanies import InsuranceCompanies

# Logging config
logger = logging.getLogger(__name__)


class PolicyRequests(Model):
    __tablename__ = 'Policy_Requests'

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('Insurance_Companies.company_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False)
    reference_no = Column(String(100), nullable=False, unique=True)
    policy_status = Column(String(10), nullable=False, default='N')
    effective_date = Column(DateTime, nullable=False)
    expire_date = Column(DateTime, nullable=False)
    premium = Column(Float, nullable=False)
    total_premium = Column(Float, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    policy_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    company = relationship('InsuranceCompanies', back_populates='policy_requests', lazy='joined')
    customer = relationship('Customers', back_populates='policy_requests', lazy='joined')

    def to_dict(self):
        logger.debug(f"Converting PolicyRequest ID {self.request_id} to dict")
        return {
            "request_id": self.request_id,
            "company_id": self.company_id,
            "customer_id": self.customer_id,
            "reference_no": self.reference_no,
            "policy_status": self.policy_status,
            "effective_date": self.effective_date.strftime('%Y-%m-%d'),
            "expire_date": self.expire_date.strftime('%Y-%m-%d'),
            "premium": self.premium,
            "total_premium": self.total_premium,
            "transaction_type": self.transaction_type,
            "policy_response": self.policy_response,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# === Token Utilities ===

def get_api_token(company_id):
    logger.debug(f"Fetching API token for company_id={company_id}")
    company = InsuranceCompanies.query.get(company_id)
    if not company:
        raise ValueError("Company not found")

    if company.is_token_valid():
        return company.api_token

    logger.info(f"Refreshing token for company_id={company_id}")
    token_response = refresh_token(
        company.api_base_url,
        company.partner_code,
        company.agent_code
    )
    company.refresh_token(
        new_token=token_response['token'],
        expiration=datetime.strptime(token_response['expiration'], '%Y-%m-%dT%H:%M:%S')
    )
    return company.api_token


# === Main Service Function ===

def create_policy_request(customer_id, company_id, request_data):
    logger.debug(f"Creating policy request for customer_id={customer_id}, company_id={company_id}")
    try:
        token = get_api_token(company_id)
        company = InsuranceCompanies.query.get(company_id)
        if not company:
            raise ValueError("Insurance company not found")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        api_url = f"{company.api_base_url}/CreatePolicy"
        logger.debug(f"Sending request to {api_url}")
        response = requests.post(api_url, headers=headers, json=request_data)

        if response.status_code != 200:
            raise ValueError(f"Failed to create policy: {response.text}")

        policy_request = PolicyRequests(
            customer_id=customer_id,
            company_id=company_id,
            reference_no=request_data['ReferenceNo'],
            policy_status=request_data['PolicyStatus'],
            effective_date=datetime.strptime(request_data['EffectiveDate'], '%Y-%m-%d'),
            expire_date=datetime.strptime(request_data['ExpireDate'], '%Y-%m-%d'),
            premium=request_data['Premium'],
            total_premium=request_data['TotalPremium'],
            transaction_type=request_data['TransactionType'],
            policy_response=response.text
        )

        db.session.add(policy_request)
        db.session.commit()
        logger.info(f"PolicyRequest created successfully: request_id={policy_request.request_id}")
        return policy_request

    except Exception as e:
        db.session.rollback()
        logger.exception("Error during create_policy_request")
        raise
