# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/insurance_preparation_service.py
from backend.models.InsurancePreparation import InsurancePreparation
from backend import db
import logging
import json

# Initialize Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class InsurancePreparationService:
    @staticmethod
    def create_preparation(
        user_id,
        insured_info=None,
        motor_info=None,
        policy_info=None,
        driver_info=None,
        beneficiary_info=None,
        coverage_info=None,
        consent_info=None,
    ):
        """
        Create a new insurance preparation record.

        Args:
            user_id (int): ID of the user creating the preparation.
            insured_info (dict): Insured details.
            motor_info (dict): Motor details.
            policy_info (dict): Policy details.
            driver_info (dict): Driver details.
            beneficiary_info (dict): Beneficiary details.
            coverage_info (dict): Coverage details.
            consent_info (dict): Consent details.

        Returns:
            InsurancePreparation: The created preparation record.

        Raises:
            Exception: If there is any issue during the creation process.
        """
        try:
            logger.debug(f"🔄 Creating preparation for user_id={user_id}, "
                         f"insured_info={insured_info}, motor_info={motor_info}, "
                         f"policy_info={policy_info}, driver_info={driver_info}, "
                         f"beneficiary_info={beneficiary_info}, coverage_info={coverage_info}, "
                         f"consent_info={consent_info}")

            if not user_id:
                logger.error("❌ User ID is missing for preparation creation.")
                raise ValueError("User ID is required to create a preparation.")

            preparation = InsurancePreparation(
                user_id=user_id,
                insured_info=json.dumps(insured_info) if isinstance(insured_info, dict) else insured_info,
                motor_info=json.dumps(motor_info) if isinstance(motor_info, dict) else motor_info,
                policy_info=json.dumps(policy_info) if isinstance(policy_info, dict) else policy_info,
                driver_info=json.dumps(driver_info) if isinstance(driver_info, dict) else driver_info,
                beneficiary_info=json.dumps(beneficiary_info) if isinstance(beneficiary_info, dict) else beneficiary_info,
                coverage_info=json.dumps(coverage_info) if isinstance(coverage_info, dict) else coverage_info,
                consent_info=json.dumps(consent_info) if isinstance(consent_info, dict) else consent_info,
            )

            db.session.add(preparation)
            db.session.commit()

            logger.info(f"✅ Preparation created successfully: {preparation}")
            return preparation
        except Exception as e:
            logger.exception(f"❌ Error creating preparation for user_id={user_id}: {e}")
            db.session.rollback()
            raise e

    @staticmethod
    def get_preparation_by_user(user_id):
        """
        Retrieve the insurance preparation for a specific user.

        Args:
            user_id (int): ID of the user.

        Returns:
            InsurancePreparation or None: The retrieved preparation record or None if not found.

        Raises:
            Exception: If there is any issue during the retrieval process.
        """
        try:
            logger.debug(f"🔍 Retrieving preparation for user_id={user_id}")
            
            if not user_id:
                logger.error("❌ User ID is missing for preparation retrieval.")
                raise ValueError("User ID is required to retrieve preparation.")

            preparation = InsurancePreparation.query.filter_by(user_id=user_id).first()
            if not preparation:
                logger.warning(f"⚠️ No preparation found for user_id={user_id}")
                return None

            logger.info(f"✅ Preparation retrieved for user_id={user_id}: {preparation}")
            return preparation
        except Exception as e:
            logger.exception(f"❌ Error retrieving preparation for user_id={user_id}: {e}")
            raise e

    @staticmethod
    def update_preparation(preparation_id, updates):
        """
        Update an existing insurance preparation record.

        Args:
            preparation_id (int): ID of the preparation to update.
            updates (dict): Fields and values to update.

        Returns:
            InsurancePreparation: The updated preparation record.

        Raises:
            Exception: If there is any issue during the update process.
        """
        try:
            logger.debug(f"🔄 Updating preparation with id={preparation_id}, updates={updates}")
            
            if not preparation_id:
                logger.error("❌ Preparation ID is missing for update.")
                raise ValueError("Preparation ID is required to update preparation.")

            preparation = InsurancePreparation.query.get(preparation_id)
            if not preparation:
                logger.warning(f"⚠️ Preparation not found with id={preparation_id}")
                raise ValueError("Preparation not found")

            for key, value in updates.items():
                if hasattr(preparation, key):
                    setattr(preparation, key, json.dumps(value) if isinstance(value, dict) else value)
                    logger.debug(f"🔄 Updated field '{key}' with value '{value}'")

            db.session.commit()

            logger.info(f"✅ Preparation updated successfully with id={preparation_id}: {preparation}")
            return preparation
        except Exception as e:
            logger.exception(f"❌ Error updating preparation with id={preparation_id}: {e}")
            db.session.rollback()
            raise e

    @staticmethod
    def delete_preparation(preparation_id):
        """
        Delete an insurance preparation record by its ID.

        Args:
            preparation_id (int): ID of the preparation to delete.

        Returns:
            None

        Raises:
            Exception: If there is any issue during the deletion process.
        """
        try:
            logger.debug(f"🔄 Attempting to delete preparation with id={preparation_id}")
            
            if not preparation_id:
                logger.error("❌ Preparation ID is missing for deletion.")
                raise ValueError("Preparation ID is required to delete preparation.")

            preparation = InsurancePreparation.query.get(preparation_id)
            if not preparation:
                logger.warning(f"⚠️ Preparation not found with id={preparation_id}")
                raise ValueError("Preparation not found")

            db.session.delete(preparation)
            db.session.commit()

            logger.info(f"✅ Preparation deleted successfully with id={preparation_id}")
        except Exception as e:
            logger.exception(f"❌ Error deleting preparation with id={preparation_id}: {e}")
            db.session.rollback()
            raise e
