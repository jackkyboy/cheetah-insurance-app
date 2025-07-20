# /Users/apichet/Downloads/cheetah-insurance-app/backend/models/Documents.py
import logging
import os
from datetime import datetime
from backend.db import db, Model, Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey, relationship

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Documents(Model):
    """
    Represents a document associated with a customer.
    """
    __tablename__ = 'Documents'

    # Primary Key
    document_id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary key for Documents table")

    # Foreign Key
    customer_id = Column(Integer, ForeignKey('Customers.customer_id'), nullable=False, comment="Foreign key to Customers table")

    # Metadata
    document_type = Column(String(100), nullable=False, comment="Type of the document (e.g., ID_CARD, CAR_REGISTRATION)")
    file_path = Column(String(255), nullable=False, comment="File path where the document is stored")
    ocr_data = Column(JSON, nullable=True, comment="OCR data extracted from the document, if available")
    processed = Column(Boolean, default=False, comment="Indicates if OCR processing has been completed")
    uploaded_at = Column(DateTime, default=datetime.utcnow, comment="Timestamp when the document was uploaded")

    # New field
    status = Column(String(50), default="uploaded", nullable=False, comment="Status of the document (e.g., uploaded, verified)")

    # Relationship
    customer = relationship('Customers', back_populates='documents', lazy='select')

    def to_dict(self):
        try:
            logger.debug(f"Converting document_id={self.document_id} to dictionary")
            file_name = os.path.basename(self.file_path) if self.file_path else None
            file_url = f"/api/documents/uploads/{file_name}" if file_name else None
            return {
                'document_id': self.document_id,
                'customer_id': self.customer_id,
                'document_type': self.document_type,
                'file_path': self.file_path,
                'file_name': file_name,
                'file_url': file_url,
                'ocr_data': self.ocr_data,
                'processed': self.processed,
                'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if self.uploaded_at else None
            }
        except Exception as e:
            logger.error(f"Error converting document to dictionary: {e}")
            raise ValueError("Failed to serialize document data")


# Service Functions

def upload_document(customer_id, document_type, file_path, ocr_data=None):
    try:
        logger.debug(f"Uploading document for customer_id={customer_id}, type={document_type}")
        new_document = Documents(
            customer_id=customer_id,
            document_type=document_type,
            file_path=file_path,
            ocr_data=ocr_data,
            processed=bool(ocr_data)
        )
        db.session.add(new_document)
        db.session.commit()
        logger.info(f"Document uploaded successfully: {new_document.document_id}")
        return new_document.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.exception("Error uploading document")
        raise Exception(f"Error uploading document: {str(e)}")


def get_documents_by_customer(customer_id):
    try:
        logger.debug(f"Fetching documents for customer_id={customer_id}")
        documents = Documents.query.filter_by(customer_id=customer_id).all()
        if not documents:
            logger.warning(f"No documents found for customer_id={customer_id}")
            return []
        return [doc.to_dict() for doc in documents]
    except Exception as e:
        logger.exception("Error fetching documents")
        raise Exception(f"Error fetching documents: {str(e)}")


def delete_document(document_id):
    try:
        logger.debug(f"Deleting document with ID: {document_id}")
        document = Documents.query.get(document_id)
        if not document:
            logger.warning(f"Document not found: {document_id}")
            raise ValueError("Document not found")

        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            logger.debug(f"File deleted: {document.file_path}")
        else:
            logger.warning(f"File not found for deletion: {document.file_path}")

        db.session.delete(document)
        db.session.commit()
        logger.info(f"Document deleted successfully: {document_id}")
        return {"message": "Document deleted successfully"}
    except Exception as e:
        db.session.rollback()
        logger.exception("Error deleting document")
        raise Exception(f"Error deleting document: {str(e)}")
