from datetime import datetime
import logging
import requests  # Ensure requests library is installed and imported
from backend.models import db
from backend.models.InsuranceCompanies import InsuranceCompanies  # Import InsuranceCompanies for token management

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PolicyRequests(db.Model):
    __tablename__ = 'Policy_Requests'

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('Insurance_Companies.company_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False)
    reference_no = db.Column(db.String(100), nullable=False, unique=True)
    policy_status = db.Column(db.String(10), nullable=False, default='N')
    effective_date = db.Column(db.DateTime, nullable=False)
    expire_date = db.Column(db.DateTime, nullable=False)
    premium = db.Column(db.Float, nullable=False)
    total_premium = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    policy_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    company = db.relationship('InsuranceCompanies', back_populates='policy_requests', lazy='joined')
    customer = db.relationship('Customers', back_populates='policy_requests', lazy='joined')

    def to_dict(self):
        """
        Convert Policy Request data to a dictionary.
        """
        logger.debug(f"Converting Policy Request ID {self.request_id} to dictionary.")
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


# Helper function for refreshing API token
def get_api_token(company_id):
    """
    Retrieve a valid API token for the given company.
    Refreshes the token if it's expired.
    """
    logger.debug(f"Fetching API token for company_id={company_id}")
    company = InsuranceCompanies.query.get(company_id)
    if not company:
        logger.error(f"Company not found for company_id={company_id}")
        raise ValueError("Company not found")

    if company.is_token_valid():
        logger.debug(f"Token for company_id={company_id} is valid.")
        return company.api_token

    logger.info(f"Token expired for company_id={company_id}, refreshing token...")
    token_response = refresh_token(company.api_base_url, company.partner_code, company.agent_code)
    company.refresh_token(
        new_token=token_response['token'],
        expiration=datetime.strptime(token_response['expiration'], '%Y-%m-%dT%H:%M:%S')
    )
    return company.api_token


# Function to create a Policy Request
def create_policy_request(customer_id, company_id, request_data):
    """
    Create a Policy Request and send it to the insurance company's API.
    """
    logger.debug(f"Creating policy request for customer_id={customer_id}, company_id={company_id}")
    try:
        token = get_api_token(company_id)
        company = InsuranceCompanies.query.get(company_id)

        if not company:
            logger.error(f"Insurance company not found for company_id={company_id}")
            raise ValueError("Insurance company not found")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Send POST Request to the insurance company's API
        logger.debug(f"Sending policy request to {company.api_base_url}/CreatePolicy")
        response = requests.post(
            url=f"{company.api_base_url}/CreatePolicy",
            headers=headers,
            json=request_data
        )

        # Check the response status
        if response.status_code != 200:
            logger.error(f"Failed to create policy: {response.text}")
            raise ValueError(f"Failed to create policy: {response.text}")

        # Save the request to the database
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
            policy_response=response.json()
        )
        db.session.add(policy_request)
        db.session.commit()

        logger.info(f"Policy request created successfully for customer_id={customer_id}, request_id={policy_request.request_id}")
        return policy_request

    except Exception as e:
        logger.exception(f"Error creating policy request for customer_id={customer_id}")
        raise e
