# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/policy_service.py
from backend.models.CustomerPolicies import CustomerPolicies
from backend import db
import logging

# Initialize Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class PolicyService:
    @staticmethod
    def create_policy(customer_id, package_id, policy_number=None, insurance_response=None):
        """
        Create a new policy for a customer.
        """
        try:
            logger.debug(f"🔄 Creating policy for customer_id={customer_id}, package_id={package_id}")
            new_policy = CustomerPolicies(
                customer_id=customer_id,
                package_id=package_id,
                status='pending',  # Default status
                policy_number=policy_number,
                insurance_company_response=insurance_response
            )
            db.session.add(new_policy)
            db.session.commit()

            logger.info(f"✅ Policy created successfully: {new_policy}")
            return new_policy
        except Exception as e:
            logger.exception(f"❌ Error creating policy for customer_id={customer_id}: {e}")
            db.session.rollback()
            raise Exception(f"Error creating policy: {str(e)}")

    @staticmethod
    def get_policy_by_id(policy_id):
        """
        Retrieve a policy by its ID.
        """
        try:
            logger.debug(f"🔍 Retrieving policy with ID={policy_id}")
            policy = CustomerPolicies.query.get(policy_id)
            if not policy:
                logger.warning(f"⚠️ Policy not found with ID={policy_id}")
                raise ValueError(f"Policy with ID {policy_id} not found.")
            logger.info(f"✅ Policy retrieved: {policy}")
            return policy
        except Exception as e:
            logger.exception(f"❌ Error retrieving policy with ID={policy_id}: {e}")
            raise e

    @staticmethod
    def get_policies_by_customer(customer_id):
        """
        Retrieve all policies for a customer.
        """
        try:
            logger.debug(f"🔍 Retrieving policies for customer_id={customer_id}")
            policies = CustomerPolicies.query.filter_by(customer_id=customer_id).all()
            result = [
                {
                    'policy_id': policy.policy_id,
                    'customer_id': policy.customer_id,
                    'package_id': policy.package_id,
                    'request_date': policy.request_date,
                    'status': policy.status,
                    'policy_number': policy.policy_number,
                    'insurance_company_response': policy.insurance_company_response,
                }
                for policy in policies
            ]
            logger.info(f"✅ Retrieved {len(result)} policies for customer_id={customer_id}")
            return result
        except Exception as e:
            logger.exception(f"❌ Error fetching policies for customer_id={customer_id}: {e}")
            raise e

    @staticmethod
    def update_policy_status(policy_id, status, policy_number=None, insurance_response=None):
        """
        Update the status of a policy.
        """
        try:
            logger.debug(f"🔄 Updating policy with ID={policy_id}, status={status}")
            policy = CustomerPolicies.query.get(policy_id)
            if not policy:
                logger.warning(f"⚠️ Policy not found with ID={policy_id}")
                raise ValueError(f"Policy with ID {policy_id} not found.")

            policy.status = status
            if policy_number:
                policy.policy_number = policy_number
            if insurance_response:
                policy.insurance_company_response = insurance_response
            db.session.commit()

            logger.info(f"✅ Policy updated successfully: {policy}")
            return policy
        except Exception as e:
            logger.exception(f"❌ Error updating policy with ID={policy_id}: {e}")
            db.session.rollback()
            raise e

    @staticmethod
    def delete_policy(policy_id):
        """
        Delete a policy by its ID.
        """
        try:
            logger.debug(f"🔄 Attempting to delete policy with ID={policy_id}")
            policy = CustomerPolicies.query.get(policy_id)
            if not policy:
                logger.warning(f"⚠️ Policy not found with ID={policy_id}")
                raise ValueError(f"Policy with ID {policy_id} not found.")

            db.session.delete(policy)
            db.session.commit()
            logger.info(f"✅ Policy deleted successfully with ID={policy_id}")
        except Exception as e:
            logger.exception(f"❌ Error deleting policy with ID={policy_id}: {e}")
            db.session.rollback()
            raise e

    @staticmethod
    def validate_policy(policy_id=None, policy_number=None, customer_id=None):
        """
        Validate whether a policy exists and belongs to a specific customer.
        """
        try:
            logger.debug(f"🔍 Validating policy with policy_id={policy_id}, policy_number={policy_number}, customer_id={customer_id}")
            query = CustomerPolicies.query
            if policy_id:
                query = query.filter_by(policy_id=policy_id)
            if policy_number:
                query = query.filter_by(policy_number=policy_number)
            if customer_id:
                query = query.filter_by(customer_id=customer_id)

            policy = query.first()
            if not policy:
                logger.warning(f"⚠️ Policy validation failed.")
                raise ValueError("Policy not found or unauthorized access.")
            logger.info(f"✅ Policy validated: {policy}")
            return policy
        except Exception as e:
            logger.exception(f"❌ Error validating policy: {e}")
            raise e
