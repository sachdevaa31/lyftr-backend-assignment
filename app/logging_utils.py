import json
import logging
import time
import uuid
from datetime import datetime
from fastapi import Request, Response


def setup_logger(log_level: str):
    logger = logging.getLogger("app")
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))

    logger.handlers = []
    logger.addHandler(handler)

    return logger


async def log_request(
    request: Request,
    call_next
):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    response: Response = await call_next(request)

    latency_ms = int((time.time() - start_time) * 1000)

    log_entry = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "level": "INFO",
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "latency_ms": latency_ms
    }

    logger = logging.getLogger("app")
    logger.info(json.dumps(log_entry))

    return response