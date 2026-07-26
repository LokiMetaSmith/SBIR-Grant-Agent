FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables for persistent data paths
ENV DATA_FILE=/app/data/data.json
ENV UPLOAD_FOLDER=/app/data/uploads

# Ensure the data directory exists
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "server.py"]
