# /Users/apichet/Downloads/cheetah-insurance-app/services/uploaded_documents_service.py
# /backend/services/uploaded_documents_service.py
# /backend/services/uploaded_documents_service.py

import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
from werkzeug.datastructures import FileStorage

from backend.models import db
from backend.models.Documents import Documents

# 📁 Upload Configuration
UPLOAD_DIR = os.path.abspath("uploads/documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.info(f"📁 Upload directory initialized: {UPLOAD_DIR}")

MAX_FILE_MB = 5
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}


class UploadedDocumentsService:
    """💼 Service for managing document upload, validation, retrieval, and deletion."""

    # -----------------------------
    # 🔐 Internal Utilities
    # -----------------------------
    @staticmethod
    def _generate_filename(customer_id: int, doc_type: str, original_name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = original_name.replace(" ", "_")
        return f"{customer_id}_{doc_type}_{timestamp}_{sanitized_name}"

    @staticmethod
    def _validate_file(file: FileStorage) -> None:
        if not file or "." not in file.filename:
            raise ValueError("Missing or invalid file name.")

        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type: {ext}. Allowed: {ALLOWED_EXTENSIONS}")

        file.seek(0, os.SEEK_END)
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)

        if size_mb > MAX_FILE_MB:
            raise ValueError(f"File too large: {size_mb:.2f} MB (limit is {MAX_FILE_MB} MB)")

        logger.debug(f"✅ File validated: {file.filename} ({size_mb:.2f} MB)")

    # -----------------------------
    # 📤 Upload
    # -----------------------------
    @staticmethod
    def upload_document(
        customer_id: int,
        document_type: str,
        file: FileStorage,
        ocr_data: Optional[dict] = None
    ) -> Dict:
        logger.debug(f"📤 Uploading: customer_id={customer_id}, type={document_type}, filename={file.filename}")

        if not file:
            raise ValueError("No file provided.")

        UploadedDocumentsService._validate_file(file)
        filename = UploadedDocumentsService._generate_filename(customer_id, document_type, file.filename)
        file_path = os.path.join(UPLOAD_DIR, filename)

        try:
            # 🔽 Save file
            file.save(file_path)
            logger.info(f"✅ File saved at: {file_path}")

            # 🧾 Save metadata
            document = Documents(
                customer_id=customer_id,
                document_type=document_type,
                file_path=filename,
                ocr_data=ocr_data,
                uploaded_at=datetime.utcnow(),
                status="uploaded",
                processed=bool(ocr_data)
            )

            db.session.add(document)
            db.session.commit()
            logger.info(f"✅ Document committed: {document.to_dict()}")
            return document.to_dict()

        except Exception as e:
            db.session.rollback()
            logger.exception("❌ Upload failed")
            raise Exception(f"Upload failed: {str(e)}")

    # -----------------------------
    # 📥 Fetch
    # -----------------------------
    @staticmethod
    def fetch_documents_by_customer(customer_id: int) -> List[Documents]:
        logger.debug(f"📥 Fetching documents for customer_id={customer_id}")
        try:
            if not customer_id:
                raise ValueError("Missing customer_id")

            documents = Documents.query.filter_by(customer_id=customer_id).all()
            logger.info(f"✅ Found {len(documents)} document(s)")
            return documents

        except Exception as e:
            logger.exception("❌ Fetch failed")
            raise Exception(f"Fetch failed: {str(e)}")

    # -----------------------------
    # 🗑️ Delete
    # -----------------------------
    @staticmethod
    def delete_document(document_id: int) -> Dict:
        logger.debug(f"🗑️ Deleting document_id={document_id}")

        try:
            document = Documents.query.get(document_id)
            if not document:
                raise ValueError("Document not found.")

            file_path = os.path.join(UPLOAD_DIR, document.file_path)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"🧹 File deleted: {file_path}")
            else:
                logger.warning(f"⚠️ File already missing: {file_path}")

            db.session.delete(document)
            db.session.commit()
            logger.info(f"✅ Document metadata deleted: id={document_id}")
            return {"message": "Document deleted successfully"}

        except ValueError as ve:
            db.session.rollback()
            logger.warning(f"⚠️ Deletion warning: {ve}")
            raise ve

        except Exception as e:
            db.session.rollback()
            logger.exception("❌ Delete failed")
            raise Exception(f"Delete failed: {str(e)}")
