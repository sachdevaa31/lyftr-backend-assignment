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


### API
The API will be available at:  
`http://localhost:8000`

### Stop the service
```bash
make down

### View logs
make logs



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
hex(HMAC_SHA256(secret=WEBHOOK_SECRET, message=raw_request_body))


- Signature is computed on **raw request body bytes**
- **Constant-time comparison** is used to prevent timing attacks
- Invalid or missing signatures are rejected with **HTTP 401**

---

## 7️⃣ Idempotency

- `message_id` is defined as the **primary key** in the SQLite database
- Duplicate webhook calls with the same `message_id` do not insert new rows
- Duplicate requests still return **HTTP 200** with:

```json
{ "status": "ok" }


## 8️⃣ Observability

- Structured **JSON logs** (one JSON object per request)
- Prometheus metrics for:
  - HTTP requests
  - Webhook outcomes
  - Request latency
- Health probes suitable for container orchestration

---

## 9️⃣ Design Decisions

- SQLite chosen for **simplicity and portability**
- Raw SQL used for **deterministic querying and aggregation**
- Docker Compose used for **local container orchestration**
- FastAPI chosen for **performance, async support, and built-in validation**
