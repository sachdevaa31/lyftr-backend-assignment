import hmac
import hashlib
import json
import time
from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field
from app.config import settings
from app.models import init_db
from app.storage import insert_message, list_messages, get_stats
from app.logging_utils import setup_logger, log_request
from app.metrics import (
    http_requests_total,
    webhook_requests_total,
    request_latency_ms,
    metrics_response
)

# ---------- App setup ----------
app = FastAPI()
logger = setup_logger(settings.log_level)

# Initialize DB on startup
init_db()

# Middleware for logging + metrics
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    response = await log_request(request, call_next)
    latency_ms = int((time.time() - start) * 1000)

    http_requests_total.labels(
        path=request.url.path,
        status=str(response.status_code)
    ).inc()

    request_latency_ms.observe(latency_ms)
    return response


# ---------- Models ----------
class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_msisdn: str = Field(..., alias="from", pattern=r"^\+\d+$")
    to_msisdn: str = Field(..., alias="to", pattern=r"^\+\d+$")
    ts: str = Field(..., pattern=r".*Z$")
    text: Optional[str] = Field(None, max_length=4096)


# ---------- Routes ----------

@app.post("/webhook")
async def webhook(request: Request, payload: WebhookMessage):
    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature:
        webhook_requests_total.labels(result="invalid_signature").inc()
        raise HTTPException(status_code=401, detail="invalid signature")

    expected_sig = hmac.new(
        settings.webhook_secret.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        webhook_requests_total.labels(result="invalid_signature").inc()
        raise HTTPException(status_code=401, detail="invalid signature")

    created = insert_message(
        message_id=payload.message_id,
        from_msisdn=payload.from_msisdn,
        to_msisdn=payload.to_msisdn,
        ts=payload.ts,
        text=payload.text
    )

    if created:
        webhook_requests_total.labels(result="created").inc()
    else:
        webhook_requests_total.labels(result="duplicate").inc()

    return {"status": "ok"}


@app.get("/messages")
def get_messages(
    limit: int = 50,
    offset: int = 0,
    from_filter: Optional[str] = None,
    since: Optional[str] = None,
    q: Optional[str] = None
):
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit out of range")
    if offset < 0:
        raise HTTPException(status_code=422, detail="offset out of range")

    data, total = list_messages(limit, offset, from_filter, since, q)

    return {
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/health/live")
def health_live():
    return {"status": "live"}


@app.get("/health/ready")
def health_ready():
    try:
        if not settings.webhook_secret:
            raise Exception("Missing secret")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="not ready")


@app.get("/metrics")
def metrics():
    return metrics_response()