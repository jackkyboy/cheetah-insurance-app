# ✅ Base Image
FROM python:3.10-slim

# ✅ Env Variables
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
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# ✅ Copy Python dependencies file
COPY backend/requirements.txt ./requirements.txt

# ✅ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy backend code
COPY backend /app/backend

# ✅ Expose Flask port
EXPOSE 5000

# ✅ Safety check
RUN test -f /app/backend/app.py || (echo "❌ Missing backend/app.py" && exit 1)

# ✅ Start app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.wsgi:app"]
