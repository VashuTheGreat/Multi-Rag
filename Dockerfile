FROM python:3.12-slim
sudo apt-get update && sudo apt-get      │ │
│ │ install -y tesseract-ocr                 │ │
│ │ libtesseract-dev poppler-utils           │ │
│ │ libmagic-dev      

WORKDIR /app

# Copy dependency files first (better caching)
COPY requirements.txt pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]