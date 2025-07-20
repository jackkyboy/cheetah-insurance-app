# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/ClaimIssues.py
import logging
from backend.db import (
    db, Model, Column, Integer, String, DateTime, Text, ForeignKey, relationship
)

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ClaimIssues(Model):
    __tablename__ = 'Claim_Issues'

    issue_id = Column(Integer, primary_key=True, autoincrement=True)

    policy_id = Column(
        Integer,
        ForeignKey('Customer_Policies.policy_id'),
        nullable=True,
        comment="Foreign key referencing Customer_Policies. Nullable for general claims."
    )

    user_id = Column(
        Integer,
        ForeignKey('Users.user_id'),
        nullable=False,
        comment="Foreign key referencing Users"
    )

    issue_description = Column(
        Text,
        nullable=False,
        comment="Detailed description of the issue"
    )

    issue_date = Column(
        DateTime,
        default=db.func.now(),
        comment="Date when the issue was reported"
    )

    status = Column(
        String(50),
        default='pending',
        comment="Status of the issue (e.g., pending, resolved, escalated)"
    )

    insurance_response = Column(
        Text,
        nullable=True,
        comment="Response from the insurance company"
    )

    resolution_date = Column(
        DateTime,
        nullable=True,
        comment="Date when the issue was resolved"
    )

    # Relationships
    policy = relationship(
        'CustomerPolicies',
        backref='claim_issues',
        lazy=True
    )

    user = relationship(
        'Users',
        backref='claim_issues',
        lazy=True
    )

    def to_dict(self):
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
