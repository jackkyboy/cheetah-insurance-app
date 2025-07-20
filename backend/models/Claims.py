from datetime import datetime
from backend.db import (
    db, Model, Column, Integer, String, DateTime, Float, Text, ForeignKey, relationship
)


class Claims(Model):
    """
    Represents a claim in the insurance system. Claims are associated with a policy
    (if applicable) and a specific user.
    """
    __tablename__ = 'Claims'

    # Columns
    claim_id = Column(Integer, primary_key=True, autoincrement=True)

    policy_id = Column(
        Integer,
        ForeignKey('Customer_Policies.policy_id'),
        nullable=True
    )

    user_id = Column(
        Integer,
        ForeignKey('Users.user_id'),
        nullable=False
    )

    claim_date = Column(
        DateTime,
        default=db.func.now()
    )

    claim_status = Column(
        String(50),
        default='Pending'
    )

    claim_amount = Column(
        Float,
        nullable=True
    )

    claim_description = Column(
        Text,
        nullable=False
    )

    resolution_date = Column(
        DateTime,
        nullable=True
    )

    # Relationships
    policy = relationship(
        'CustomerPolicies',
        backref='claims',
        lazy='joined'
    )

    user = relationship(
        'Users',
        backref='claims',
        lazy='joined'
    )

    def to_dict(self):
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
