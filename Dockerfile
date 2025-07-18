# Base image
FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY templates templates
COPY app.py app.py
COPY models.py models.py
COPY docker-compose.yml docker-compose.yml


# Default command
CMD ["python", "app.py"]
