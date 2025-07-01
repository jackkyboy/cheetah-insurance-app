# ✅ ใช้ Python Slim /Users/apichet/Downloads/cheetah-insurance-app/backend/Dockerfile
# ✅ ใช้ Python 3.10 Slim เป็น Base Image
FROM python:3.10-slim

# ✅ ENV: ตั้งค่าระบบพื้นฐาน
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    GOOGLE_APPLICATION_CREDENTIALS=/app/backend/config/credentials.json

# ✅ ทำงานใน /app
WORKDIR /app

# ✅ ติดตั้งระบบที่จำเป็น (เช่น OCR, curl)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-tha \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ✅ ติดตั้ง Python packages จาก requirements.txt
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Copy ทั้งโปรเจคเข้า container
COPY . /app

# ✅ ตรวจสอบว่า backend/__init__.py มีจริง
RUN test -f backend/__init__.py || (echo "❌ missing backend/__init__.py" && exit 1)

# ✅ เปิดพอร์ต Gunicorn (Flask API)
EXPOSE 5000

# ✅ สั่งรัน Gunicorn ด้วยโมดูล backend.wsgi:app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.wsgi:app"]
