# /Users/apichet/Downloads/cheetah-insurance-app/backend/services/document_service.py
from backend.models.Documents import Documents
from backend import db
import pytesseract
from PIL import Image
import os

# 🔥 กำหนดค่าพาธของ Tesseract OCR (แก้ไขเป็นพาธที่ถูกต้องในระบบของคุณ)
pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"  # ตรวจสอบให้แน่ใจว่า Tesseract ติดตั้งถูกต้อง

# 🔥 กำหนดโฟลเดอร์ที่ใช้เก็บไฟล์อัปโหลด
UPLOAD_DIR = "/Users/apichet/Downloads/cheetah-insurance-app/backend/uploads/documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)


class DocumentService:
    @staticmethod
    def upload_document(customer_id, document_type, file_path):
        """
        อัปโหลดเอกสารใหม่ พร้อมทำ OCR (ถ้ามี)
        """
        try:
            if not customer_id:
                raise ValueError("❌ Missing required field: customer_id")

            full_file_path = os.path.join(UPLOAD_DIR, file_path)

            # ✅ ตรวจสอบว่าไฟล์มีอยู่จริง
            if not os.path.exists(full_file_path):
                raise FileNotFoundError(f"File not found: {full_file_path}")

            # ✅ ทำ OCR ถ้า document_type รองรับ
            ocr_text = None
            if document_type in ["id_card", "driver_license", "car_registration"]:
                ocr_text = DocumentService.perform_ocr(full_file_path)

            # ✅ บันทึกข้อมูลเอกสารลงในฐานข้อมูล
            new_document = Documents(
                customer_id=customer_id,
                document_type=document_type,
                file_path=file_path,
                ocr_data=ocr_text,  # เปลี่ยนให้ตรงกับ Model
                processed=bool(ocr_text)  # หาก OCR สำเร็จให้ processed=True
            )
            db.session.add(new_document)
            db.session.commit()

            return {
                "document_id": new_document.document_id,
                "customer_id": new_document.customer_id,
                "document_type": new_document.document_type,
                "file_path": new_document.file_path,
                "ocr_data": new_document.ocr_data,
                "uploaded_at": new_document.uploaded_at
            }
        except ValueError as ve:
            db.session.rollback()
            raise ValueError(f"Validation Error: {str(ve)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error uploading document: {str(e)}")

    @staticmethod
    def perform_ocr(file_path):
        """
        ดึงข้อความจากไฟล์ภาพด้วย OCR
        """
        try:
            valid_extensions = {".jpg", ".jpeg", ".png"}
            ext = os.path.splitext(file_path)[-1].lower()
            if ext not in valid_extensions:
                raise ValueError(f"Unsupported file type: {ext}")

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang="tha+eng")
            return text.strip()
        except Exception as e:
            raise Exception(f"Error performing OCR: {str(e)}")

    @staticmethod
    def get_documents_by_customer(customer_id):
        """
        ดึงข้อมูลเอกสารของลูกค้า
        """
        try:
            if not customer_id:
                raise ValueError("❌ Missing customer_id for document fetching")

            documents = Documents.query.filter_by(customer_id=customer_id).all()
            if not documents:
                raise ValueError("No documents found for the given customer_id")

            return [{
                "document_id": doc.document_id,
                "document_type": doc.document_type,
                "file_path": doc.file_path,
                "ocr_data": doc.ocr_data,
                "processed": doc.processed,
                "uploaded_at": doc.uploaded_at
            } for doc in documents]
        except Exception as e:
            raise Exception(f"Error fetching documents: {str(e)}")

    @staticmethod
    def delete_document(document_id):
        """
        ลบเอกสาร
        """
        try:
            document = Documents.query.get(document_id)
            if not document:
                raise ValueError("Document not found")

            file_path = os.path.join(UPLOAD_DIR, document.file_path)

            # ✅ ลบไฟล์ในระบบ (ถ้ามี)
            if os.path.exists(file_path):
                os.remove(file_path)

            # ✅ ลบข้อมูลในฐานข้อมูล
            db.session.delete(document)
            db.session.commit()
            return {"message": "Document deleted successfully"}
        except ValueError as ve:
            db.session.rollback()
            raise ValueError(f"❌ Validation Error: {str(ve)}")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error deleting document: {str(e)}")
