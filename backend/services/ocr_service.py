from PIL import Image
import pytesseract
import re

def process_ocr(file_path, document_type):
    """
    ดึงข้อมูลจากไฟล์เอกสารด้วย OCR ตามประเภทเอกสารที่กำหนด
    """
    text = pytesseract.image_to_string(Image.open(file_path), lang='tha+eng')

    # แยกการประมวลผลตามประเภทเอกสาร
    if document_type == "id_card":
        return extract_id_card_info(text)
    elif document_type == "driving_license":
        return extract_driving_license_info(text)
    elif document_type == "insurance_policy":
        return extract_insurance_policy_info(text)
    elif document_type == "bank_book":
        return extract_bank_book_info(text)
    elif document_type == "repair_invoice":
        return extract_repair_invoice_info(text)
    else:
        raise ValueError("Unsupported document type")

def extract_id_card_info(text):
    return {
        "id_card_number": extract_pattern(text, r"\b\d{13}\b"),
        "name": extract_pattern(text, r"นาย\s\w+\s\w+|นาง\s\w+\s\w+"),
        "birth_date": extract_pattern(text, r"\d{2}\s\w+\s\d{4}")
    }

def extract_driving_license_info(text):
    return {
        "license_number": extract_pattern(text, r"\d{6,10}"),
        "name": extract_pattern(text, r"Name:\s\w+\s\w+"),
        "expiration_date": extract_pattern(text, r"\d{2}\s\w+\s\d{4}")
    }

def extract_insurance_policy_info(text):
    return {
        "policy_number": extract_pattern(text, r"เลขที่กรมธรรม์:\s\d+"),
        "car_registration": extract_pattern(text, r"ทะเบียน:\s\w+-\d+"),
        "coverage_period": extract_pattern(text, r"วันที่เริ่ม:\s\d{2}/\d{2}/\d{4}")
    }

def extract_bank_book_info(text):
    return {
        "account_number": extract_pattern(text, r"\d{3}-\d{1}-\d{5}-\d{1}"),
        "bank_name": extract_pattern(text, r"ธนาคาร\s\w+"),
        "branch_name": extract_pattern(text, r"สาขา\s\w+")
    }

def extract_repair_invoice_info(text):
    return {
        "invoice_number": extract_pattern(text, r"เลขที่ใบเสร็จ:\s\d+"),
        "total_amount": extract_pattern(text, r"รวมเงิน\s\d+\.\d{2}"),
        "date": extract_pattern(text, r"\d{2}/\d{2}/\d{4}")
    }

def extract_pattern(text, pattern):
    match = re.search(pattern, text)
    return match.group() if match else None
