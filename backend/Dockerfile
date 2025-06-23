FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

# Install ffmpeg for audio/video processing
RUN apt-get update && apt-get install -y ffmpeg \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --default-timeout=100 -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p temp

# Create a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
