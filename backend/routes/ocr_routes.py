from flask import Blueprint, request, jsonify
from backend.services.ocr_service import process_ocr
import os

ocr_bp = Blueprint("ocr", __name__)

@ocr_bp.route("/process", methods=["POST"])
def process_document():
    """
    รับไฟล์เอกสารจากลูกค้าและประมวลผล OCR
    """
    try:
        # รับไฟล์จาก request
        file = request.files.get("file")
        document_type = request.form.get("document_type")

        if not file or not document_type:
            return jsonify({"error": "Missing file or document type"}), 400

        # บันทึกไฟล์ลงชั่วคราว
        upload_folder = "./uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # ประมวลผล OCR
        extracted_data = process_ocr(file_path, document_type)

        return jsonify({"message": "Document processed successfully", "data": extracted_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
