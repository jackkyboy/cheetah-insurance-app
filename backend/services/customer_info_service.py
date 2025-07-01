# /Users/apichet/Downloads/cheetah-insurance-app/services/customer_info_service.py
import logging
import re
from backend.models.CustomerInfo import CustomerInfo
from backend.models.Customers import Customers
from backend import db
from sqlalchemy.orm import joinedload

# ตั้งค่า Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CustomerInfoService:
    @staticmethod
    def create_customer_info(customer_id, id_card_number=None, driver_license_number=None,
                            vehicle_registration=None, policy_number=None, extracted_from="manual"):
        """
        เพิ่มข้อมูลลูกค้าใหม่
        """
        logger.info(f"Creating customer info for customer_id: {customer_id}")
        try:
            # ตรวจสอบว่ามี customer_id หรือไม่
            customer = Customers.query.get(customer_id)
            if not customer:
                logger.warning(f"Customer not found for customer_id: {customer_id}")
                raise ValueError("Customer not found.")

            new_info = CustomerInfo(
                customer_id=customer_id,
                id_card_number=id_card_number,
                driver_license_number=driver_license_number,
                vehicle_registration=vehicle_registration,
                policy_number=policy_number,
                extracted_from=extracted_from
            )
            db.session.add(new_info)
            db.session.commit()
            logger.info(f"Customer info created successfully: {new_info.info_id}")
            return {
                "info_id": new_info.info_id,
                "customer_id": new_info.customer_id,
                "id_card_number": new_info.id_card_number,
                "driver_license_number": new_info.driver_license_number,
                "vehicle_registration": new_info.vehicle_registration,
                "policy_number": new_info.policy_number,
                "extracted_from": new_info.extracted_from,
                "created_at": new_info.created_at
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating customer info: {str(e)}")
            raise Exception(f"Error creating customer info: {str(e)}")

    @staticmethod
    def get_customer_info(customer_id):
        """
        ดึงข้อมูลลูกค้า พร้อมข้อมูล Customers แบบ Eager Loading
        """
        logger.info(f"Fetching customer info for customer_id: {customer_id}")
        try:
            info = CustomerInfo.query.options(
                joinedload(CustomerInfo.customer)  # ใช้ Eager Loading
            ).filter_by(customer_id=customer_id).first()

            if not info:
                logger.warning(f"No customer info found for customer_id: {customer_id}")
                raise ValueError("Customer info not found.")

            return {
                "info_id": info.info_id,
                "customer_id": info.customer_id,
                "id_card_number": info.id_card_number,
                "driver_license_number": info.driver_license_number,
                "vehicle_registration": info.vehicle_registration,
                "policy_number": info.policy_number,
                "extracted_from": info.extracted_from,
                "created_at": info.created_at,
                "customer": {
                    "first_name": info.customer.first_name,
                    "last_name": info.customer.last_name,
                    "email": info.customer.email,
                    "phone_number": info.customer.phone_number
                }
            }
        except Exception as e:
            logger.error(f"Error fetching customer info: {str(e)}")
            raise Exception(f"Error fetching customer info: {str(e)}")

    @staticmethod
    def validate_info(id_card_number=None, driver_license_number=None, vehicle_registration=None):
        """
        ตรวจสอบความถูกต้องของข้อมูล
        """
        errors = []
        logger.info("Validating customer info data...")
        if id_card_number and not re.match(r'^\d{13}$', id_card_number):
            errors.append("ID card number must be 13 digits.")
        if driver_license_number and not re.match(r'^\w{5,15}$', driver_license_number):
            errors.append("Driver license number is invalid.")
        if vehicle_registration and not re.match(r'^[A-Z0-9\s-]+$', vehicle_registration):
            errors.append("Vehicle registration is invalid.")

        if errors:
            logger.warning(f"Validation errors found: {errors}")
        return errors

    @staticmethod
    def process_ocr_results(customer_id, ocr_data):
        """
        ประมวลผลข้อมูลจาก OCR และบันทึกลงฐานข้อมูล
        """
        logger.info(f"Processing OCR results for customer_id: {customer_id}")
        errors = CustomerInfoService.validate_info(
            id_card_number=ocr_data.get("id_card_number"),
            driver_license_number=ocr_data.get("driver_license_number"),
            vehicle_registration=ocr_data.get("vehicle_registration")
        )

        if errors:
            logger.error(f"OCR Validation Errors: {errors}")
            return {"errors": errors}

        try:
            result = CustomerInfoService.create_customer_info(
                customer_id=customer_id,
                id_card_number=ocr_data.get("id_card_number"),
                driver_license_number=ocr_data.get("driver_license_number"),
                vehicle_registration=ocr_data.get("vehicle_registration"),
                policy_number=ocr_data.get("policy_number"),
                extracted_from="OCR"
            )
            logger.info(f"OCR results processed successfully for customer_id: {customer_id}")
            return result
        except Exception as e:
            logger.error(f"Error processing OCR results: {str(e)}")
            raise Exception(f"Error processing OCR results: {str(e)}")
