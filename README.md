# IoT Data Pipeline with Real-Time Analytics

A scalable hybrid cloud IoT processing system that combines edge computing with AWS cloud services for real-time sensor data monitoring and visualization.

## Overview

This project implements a cost-efficient IoT data pipeline that collects, processes, and visualizes sensor data in real-time. The system uses edge devices for initial data filtering and AWS cloud services for scalable storage and analytics, optimized to minimize bandwidth costs and latency.

## Key Features

- **Hybrid Architecture**: Edge devices handle local filtering; cloud handles large-scale processing
- **Secure Communication**: MQTT over TLS for encrypted data transmission
- **Real-Time Analytics**: Live dashboards using InfluxDB and Grafana
- **Scalable Storage**: DynamoDB for primary storage, S3 for backups
- **Cost-Optimized**: Serverless design with AWS Lambda and SQS staying within free tier limits
- **Containerized Deployment**: Docker-based edge nodes for easy deployment

## Architecture Components

### Edge Layer
- Docker containerized sensor nodes
- MQTT data publishing with TLS certificates
- Local data filtering and validation

### Cloud Layer
- **AWS IoT Core**: Secure device connectivity
- **Amazon SQS**: Message queuing for reliability
- **AWS Lambda**: Serverless data processing
- **DynamoDB**: Scalable NoSQL storage
- **S3**: Long-term data backup

### Monitoring & Visualization
- **InfluxDB**: Time-series data storage
- **Grafana**: Real-time dashboards
- **Cloudflared**: Secure remote access

## Performance Metrics

- **Cost**: $0.22 USD/month for 30 days of operation
- **Throughput**: 44 messages/minute sustained
- **MQTT Messages**: 77.5k messages/month
- **Lambda Invocations**: 9.78k/month (within free tier)

## Screenshots:

- Check the screenshots folder

## Use Cases

- Smart city monitoring
- Industrial IoT systems
- Environmental sensing
- Healthcare telemetry
- Energy management

## Getting Started

The complete codebase, Docker configurations, and deployment templates are available on GitHub:

**Repository**: [github.com/Deep-Jiwan/IOTProcessing](https://github.com/Deep-Jiwan/IOTProcessing)

## Future Enhancements

- Integration with AWS SageMaker for ML/AI analytics
- Edge computing with lightweight ML models
- Multi-site deployment scaling
- Enhanced multi-tenant security
- Kubernetes orchestration for improved resource management

## Technology Stack

**Cloud Services**: AWS IoT Core, Lambda, SQS, DynamoDB, S3  
**Edge Computing**: Docker, Docker Compose  
**Monitoring**: InfluxDB, Grafana  
**Protocols**: MQTT, TLS  
**Security**: Cloudflare Zero Trust, VPN

## Current Limitations

- Tested with 12 sensors at small scale
- Requires validation for multi-site deployments
- Edge integration and fault tolerance need further optimization

---

*This project demonstrates a practical, affordable IoT monitoring solution combining the responsiveness of edge computing with the scalability of cloud services.*
