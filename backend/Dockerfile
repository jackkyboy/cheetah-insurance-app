# ✅ ใช้ Python Slim /Users/apichet/Downloads/cheetah-insurance-app/backend/Dockerfile
# ✅ ใช้ Python 3.10 Slim เป็น Base Image
# ✅ Base Image: Python 3.10 Slim
FROM python:3.10-slim

# ✅ Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    GOOGLE_APPLICATION_CREDENTIALS=/app/config/credentials.json

# ✅ Set working directory
WORKDIR /app

# ✅ Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    tesseract-ocr \
    tesseract-ocr-tha \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# ✅ Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Copy full project (including backend/, frontend/, certs/, etc.)
COPY . /app

# ✅ Safety check
RUN test -f backend/__init__.py || (echo "❌ Missing backend/__init__.py" && exit 1)

# ✅ Expose Flask API port
EXPOSE 5000

# ✅ Run app via Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.wsgi:app"]
