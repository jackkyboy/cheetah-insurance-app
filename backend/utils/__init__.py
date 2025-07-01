# /Users/apichet/Downloads/cheetah-insurance-app/utils/__init__.py
import logging
import os
import json
from flask import request, jsonify

def setup_logging(log_level=logging.DEBUG, log_file="app.log"):
    """
    ตั้งค่าระบบ Logging สำหรับแอปพลิเคชัน
    """
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # แสดง log บน console
            logging.FileHandler(log_file, mode="a", encoding="utf-8")  # บันทึก log ลงไฟล์
        ]
    )
    logging.info("Logging is set up successfully.")

def read_json_file(file_path):
    """
    อ่านไฟล์ JSON และส่งคืนข้อมูล
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error reading JSON file {file_path}: {e}")
        raise

def parse_request_body():
    """
    ดึงข้อมูล JSON จากคำขอ (request) และตรวจสอบความถูกต้อง
    """
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Invalid or missing JSON payload.")
        return data
    except Exception as e:
        logging.error(f"Error parsing request body: {e}")
        raise

def format_response(data, message="Success", status=200):
    """
    ฟอร์แมตรูปแบบการตอบกลับเป็น JSON
    """
    response = {
        "status": status,
        "message": message,
        "data": data
    }
    return jsonify(response), status

def ensure_directory_exists(directory):
    """
    ตรวจสอบว่าไดเรกทอรีมีอยู่แล้ว หากไม่มีให้สร้าง
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Directory ensured: {directory}")
    except Exception as e:
        logging.error(f"Error ensuring directory {directory}: {e}")
        raise
