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

##  INFO
- The API will be available at: http://localhost:8000 
- Stop the service : make down 
- View logs : make logs

## 4️⃣ Configuration (Environment Variables)

The application is configured using environment variables:

- **DATABASE_URL**  
  Example: `sqlite:////data/app.db`

- **WEBHOOK_SECRET**  
  Secret used to verify webhook signatures

- **LOG_LEVEL**  
  Logging level (`INFO` / `DEBUG`)

All configuration is provided via `docker-compose.yml`.

---

## 5️⃣ API Endpoints

### Health

- **GET /health/live**  
  Liveness probe. Always returns HTTP 200 once the app is running.

- **GET /health/ready**  
  Readiness probe. Returns HTTP 200 only if the database is reachable and `WEBHOOK_SECRET` is set. Otherwise returns HTTP 503.

### Webhook

- **POST /webhook**  
  Ingests WhatsApp-like messages exactly once. Validates HMAC signature and enforces idempotency.

### Messages

- **GET /messages**  
  Returns stored messages with pagination and filtering (`limit`, `offset`, `from`, `since`, `q`).

### Stats

- **GET /stats**  
  Returns message-level analytics including total messages, unique senders, top senders, and first/last timestamps.

### Metrics

- **GET /metrics**  
  Exposes Prometheus-compatible metrics.

---

## 6️⃣ HMAC Signature Verification

Webhook signatures are verified using:

