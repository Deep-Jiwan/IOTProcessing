# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables optionally.
ENV CERTS_DIR=/app/certs \
    AWS_IOT_ENDPOINT=aws.iot.ap-south-1.amazonaws.com \
    SENSOR_TYPE=temperature \
    FREQ=5 \
    RANGE= \
    LOCATION=default \
    ID=rpi \
    PYTHONUNBUFFERED=1

CMD ["python", "sensor.py"] 