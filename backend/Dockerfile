# ✅ ใช้ Python Slim /Users/apichet/Downloads/cheetah-insurance-app/backend/Dockerfile
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

# ✅ Copy full project
COPY . /app

# ✅ Safety check: Ensure backend/app.py exists
RUN test -f backend/app.py || (echo "❌ Missing backend/app.py" && exit 1)

# ✅ Expose Flask API port
EXPOSE 5000

# ✅ Run app via Gunicorn through backend.wsgi:app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.wsgi:app"]
