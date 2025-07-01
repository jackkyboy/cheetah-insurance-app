# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/ClaimIssues.py
import logging
from backend.models import db  # Import `db` from `__init__.py`

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClaimIssues(db.Model):
    __tablename__ = 'Claim_Issues'

    issue_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    policy_id = db.Column(
        db.Integer,
        db.ForeignKey('Customer_Policies.policy_id'),
        nullable=True,  # Allow policy_id to be NULL
        comment="Foreign key referencing Customer_Policies. Nullable for general claims."
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('Users.user_id'),
        nullable=False,
        comment="Foreign key referencing Users"
    )
    issue_description = db.Column(
        db.Text,
        nullable=False,
        comment="Detailed description of the issue"
    )
    issue_date = db.Column(
        db.DateTime,
        default=db.func.now(),
        comment="Date when the issue was reported"
    )
    status = db.Column(
        db.String(50),
        default='pending',
        comment="Status of the issue (e.g., pending, resolved, escalated)"
    )
    insurance_response = db.Column(
        db.Text,
        nullable=True,
        comment="Response from the insurance company"
    )
    resolution_date = db.Column(
        db.DateTime,
        nullable=True,
        comment="Date when the issue was resolved"
    )

    # Relationships
    policy = db.relationship(
        'CustomerPolicies',
        backref='claim_issues',
        lazy=True
    )
    user = db.relationship(
        'Users',
        backref='claim_issues',
        lazy=True
    )

    def to_dict(self):
        """
        Converts the ClaimIssues object into a dictionary for JSON serialization.
        """
        try:
            return {
                "issue_id": self.issue_id,
                "policy_id": self.policy_id,
                "user_id": self.user_id,
                "issue_description": self.issue_description,
                "issue_date": self.issue_date.strftime('%Y-%m-%d %H:%M:%S') if self.issue_date else None,
                "status": self.status,
                "insurance_response": self.insurance_response,
                "resolution_date": self.resolution_date.strftime('%Y-%m-%d %H:%M:%S') if self.resolution_date else None,
            }
        except Exception as e:
            logger.error(f"Error converting ClaimIssues to dictionary: {e}")
            raise ValueError("Failed to serialize ClaimIssues data")
