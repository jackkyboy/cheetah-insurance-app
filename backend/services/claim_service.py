# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/claim_service.py
from backend.models.ClaimIssues import ClaimIssues
from backend.models.CustomerPolicies import CustomerPolicies
from backend import db
import logging

logger = logging.getLogger(__name__)

class ClaimService:
    @staticmethod
    def report_claim_issue(user_id, policy_id=None, description=None, documents=None):
        """
        Report a new claim issue.
        Allows general issues without a policy_id.
        """
        try:
            logger.debug(f"Reporting claim issue: user_id={user_id}, policy_id={policy_id}")

            # Validate description
            if not description:
                raise ValueError("Description is required for reporting a claim")

            # Validate policy_id if provided
            if policy_id:
                policy = CustomerPolicies.query.filter_by(policy_id=policy_id, customer_id=user_id).first()
                if not policy:
                    logger.warning(f"Invalid or unauthorized policy_id: {policy_id} for user_id={user_id}")
                    raise ValueError("Invalid policy ID or unauthorized access")
            else:
                logger.info("No policy_id provided; proceeding as a general claim.")

            # Create a new claim issue
            new_issue = ClaimIssues(
                policy_id=policy_id,  # May be None for general claims
                user_id=user_id,
                issue_description=description,
                status="pending"
            )
            db.session.add(new_issue)

            # Handle attached documents
            if documents:
                saved_documents = []
                for document in documents:
                    file_path = f"uploads/claims/{document.filename}"
                    document.save(file_path)
                    saved_documents.append(file_path)
                logger.debug(f"Documents attached: {saved_documents}")

            db.session.commit()
            logger.info(f"Claim issue reported successfully: issue_id={new_issue.issue_id}")
            return new_issue
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error reporting claim issue: {e}")
            raise Exception(f"Error reporting claim issue: {str(e)}")

    @staticmethod
    def update_claim_status(issue_id, status, response=None, user_id=None):
        """
        Update the status of a claim issue.

        Args:
            issue_id (int): ID of the claim issue to update.
            status (str): New status for the claim issue (e.g., "resolved").
            response (str): Response or comments from the insurance team.
            user_id (int): ID of the user performing the update (for access control).

        Returns:
            ClaimIssues: The updated claim issue.
        """
        try:
            logger.debug(f"Updating claim: issue_id={issue_id}, status={status}")

            issue = ClaimIssues.query.get(issue_id)
            if not issue:
                logger.warning(f"Claim not found: issue_id={issue_id}")
                raise ValueError("Claim issue not found")

            # Ensure the user has access
            if user_id and issue.user_id != user_id:
                logger.warning(f"Unauthorized update attempt: user_id={user_id}, issue_id={issue_id}")
                raise ValueError("Unauthorized access to claim issue")

            # Update issue details
            issue.status = status
            issue.insurance_response = response
            if status == "resolved":
                issue.resolution_date = db.func.now()

            db.session.commit()
            logger.info(f"Claim updated successfully: issue_id={issue_id}, status={status}")
            return issue.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.exception(f"Error updating claim: {e}")
            raise Exception(f"Error updating claim: {str(e)}")

    @staticmethod
    def get_claim_issues_by_policy(policy_id, user_id=None):
        """
        Fetches all claim issues for a given policy.

        Args:
            policy_id (int): ID of the policy.
            user_id (int): ID of the user requesting data (for access control).

        Returns:
            list: A list of claim issues in dictionary format.
        """
        try:
            logger.debug(f"Fetching claims for policy_id={policy_id}")

            query = ClaimIssues.query.filter_by(policy_id=policy_id)
            if user_id:
                query = query.filter_by(user_id=user_id)

            issues = query.all()
            logger.info(f"Found {len(issues)} claims for policy_id={policy_id}")
            return [issue.to_dict() for issue in issues]
        except Exception as e:
            logger.exception(f"Error fetching claims: {e}")
            raise Exception(f"Error fetching claims: {str(e)}")

    @staticmethod
    def get_claim_issue_by_id(issue_id, user_id=None):
        """
        Fetches a specific claim issue by ID.

        Args:
            issue_id (int): ID of the claim issue.
            user_id (int): ID of the user requesting data (for access control).

        Returns:
            dict: A dictionary representation of the claim issue.
        """
        try:
            logger.debug(f"Fetching claim by ID: issue_id={issue_id}")

            issue = ClaimIssues.query.get(issue_id)
            if not issue:
                logger.warning(f"Claim issue not found: issue_id={issue_id}")
                raise ValueError("Claim issue not found")

            # Ensure the user has access
            if user_id and issue.user_id != user_id:
                logger.warning(f"Unauthorized access: user_id={user_id}, issue_id={issue_id}")
                raise ValueError("Unauthorized access to claim issue")

            logger.info(f"Claim fetched successfully: issue_id={issue_id}")
            return issue.to_dict()
        except Exception as e:
            logger.exception(f"Error fetching claim: {e}")
            raise Exception(f"Error fetching claim: {str(e)}")
