"""Request logging middleware extracted from auth.py for clarity."""

import time
import uuid
import logging
from datetime import datetime
from fastapi import Request

logger = logging.getLogger("api-gateway.middleware.logging")

async def request_logging_middleware(request: Request, call_next):
    """Log each request/response with timing and correlation ID."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    start_time = time.time()

    logger.info(
        "🌐 Incoming Request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": request.headers.get("content-length", 0),
            "referer": request.headers.get("referer", ""),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            "✅ Request Completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "response_size": response.headers.get("content-length", 0),
                "user_id": getattr(request.state, "user_id", None),
                "org_id": getattr(request.state, "org_id", None),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:  # pragma: no cover - passthrough logging
        process_time = time.time() - start_time
        logger.error(
            "❌ Request Failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time": round(process_time, 3),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        raise
