# Lyftr AI – Backend Assignment
Containerized Webhook API (FastAPI)

---

## 1️⃣ Overview

This project implements a production-style backend service using FastAPI that ingests WhatsApp-like messages exactly once, validates inbound requests using HMAC-based signatures, stores messages in SQLite, and exposes APIs for listing messages, analytics, health checks, and observability.

The service is fully containerized using Docker Compose and follows 12-factor application principles.

---

## 2️⃣ Tech Stack

- Language: Python 3.11
- Framework: FastAPI
- Database: SQLite
- Containerization: Docker & Docker Compose
- Metrics: Prometheus-style metrics
- Logging: Structured JSON logs

---

## 3️⃣ How to Run

### Prerequisites
- Docker Desktop
- Make

### Start the service
```bash
make up
```
