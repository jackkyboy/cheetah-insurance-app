# ✅ ใช้ Python Slim /Users/apichet/Downloads/cheetah-insurance-app/backend/Dockerfile
# ✅ ใช้ Python Slim
# ✅ ใช้ Python Slim
# ✅ ใช้ Python Slim
FROM python:3.10-slim

# ✅ ENV ตั้งค่าพื้นฐาน
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    GOOGLE_APPLICATION_CREDENTIALS=/app/backend/config/credentials.json

# ✅ Path หลัก
WORKDIR /app

# ✅ ติดตั้ง dependencies ที่จำเป็น + tesseract
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-tha \
    && rm -rf /var/lib/apt/lists/*

# ✅ ติดตั้ง Python packages
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Copy source code ทั้งหมด
COPY . /app

# ✅ ตรวจสอบว่า backend/__init__.py มีอยู่จริง
RUN test -f backend/__init__.py || (echo "❌ missing backend/__init__.py" && exit 1)

# ✅ เปิดพอร์ต Flask API
EXPOSE 5000

# ✅ เพิ่ม PYTHONPATH ซ้ำเพื่อความมั่นใจ
ENV PYTHONPATH=/app

# ✅ รัน Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.wsgi:app"]
