from backend.models import db
from datetime import datetime


class Claims(db.Model):
    """
    Represents a claim in the insurance system. Claims are associated with a policy
    (if applicable) and a specific user.
    """
    __tablename__ = 'Claims'

    # Columns
    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    policy_id = db.Column(
        db.Integer,
        db.ForeignKey('Customer_Policies.policy_id'),
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('Users.user_id'),
        nullable=False
    )
    claim_date = db.Column(
        db.DateTime,
        default=db.func.now()
    )
    claim_status = db.Column(
        db.String(50),
        default='Pending'
    )
    claim_amount = db.Column(
        db.Float,
        nullable=True
    )
    claim_description = db.Column(
        db.Text,
        nullable=False
    )
    resolution_date = db.Column(
        db.DateTime,
        nullable=True
    )

    # Relationships
    policy = db.relationship(
        'CustomerPolicies',
        backref='claims',
        lazy='joined'
    )
    user = db.relationship(
        'Users',
        backref='claims',
        lazy='joined'
    )

    def to_dict(self):
        """
        Converts the Claims object to a dictionary for JSON serialization.

        Returns:
            dict: A dictionary representation of the claim.
        """
        return {
            "claim_id": self.claim_id,
            "policy_id": self.policy_id,
            "user_id": self.user_id,
            "claim_date": self.claim_date.strftime('%Y-%m-%d %H:%M:%S'),
            "claim_status": self.claim_status,
            "claim_amount": self.claim_amount,
            "claim_description": self.claim_description,
            "resolution_date": self.resolution_date.strftime('%Y-%m-%d %H:%M:%S') if self.resolution_date else None
        }
