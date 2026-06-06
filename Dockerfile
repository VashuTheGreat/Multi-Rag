FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first
COPY requirements.txt pyproject.toml ./

# Install dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]