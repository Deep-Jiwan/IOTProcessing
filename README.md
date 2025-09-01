# IOTProcessing

This repository contains an end-to-end IoT data pipeline for collecting, processing, and storing sensor data using AWS and on-premises components.

## Overview
- **On-Prem/Sensor-Node**: Python code and Docker setup for sensor devices. Publishes sensor data to AWS IoT Core using MQTT and device certificates.
- **AWS**: Contains Lambda functions, IAM policies, and templates for processing data from IoT Core, storing in DynamoDB, backing up to S3, and forwarding to InfluxDB.
- **On-Prem/docker-compose.yaml**: Sets up local services (InfluxDB, Grafana, VPN, Cloudflared) for monitoring and secure connectivity.

## How It Works
1. **Sensor Nodes**: Run in Docker containers, read sensor values, and publish telemetry/status to AWS IoT Core using MQTT and TLS certificates.
2. **AWS IoT Core**: Routes incoming MQTT messages to SQS queues using rules.
3. **Lambda Functions**: Process SQS messages, store data in DynamoDB, forward to InfluxDB, and back up to S3.
4. **On-Prem Services**: InfluxDB and Grafana provide local monitoring and visualization of sensor data.

## Usage
1. **Sensor Node Setup**:
   - Place device certificates in `On-Prem/Sensor-Node/certs/` (do not upload to GitHub).
   - Build and run the sensor node Docker containers using `docker-compose`.
2. **AWS Setup**:
   - Deploy Lambda functions and configure IAM policies as per the templates in `AWS/`.
   - Set up IoT Core rules to forward messages to SQS.
3. **On-Prem Monitoring**:
   - Use `On-Prem/docker-compose.yaml` to start InfluxDB, Grafana, VPN, and Cloudflared for local data access and visualization.

## Security
- **Never upload certificates, private keys, or secrets to GitHub.**
- Use environment variables or `.env` files for sensitive configuration.

## Requirements
- Docker
- AWS account with IoT Core, Lambda, SQS, DynamoDB, S3
- Python 3.11 (for sensor node)

---
For details, see the code and configuration files in each folder.
