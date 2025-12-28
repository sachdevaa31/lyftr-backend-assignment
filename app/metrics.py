from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# HTTP request counter
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["path", "status"]
)

# Webhook result counter
webhook_requests_total = Counter(
    "webhook_requests_total",
    "Webhook processing results",
    ["result"]
)

# Request latency histogram
request_latency_ms = Histogram(
    "request_latency_ms",
    "Request latency in milliseconds",
    buckets=(100, 300, 500, 1000, 2000)
)


def metrics_response():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )