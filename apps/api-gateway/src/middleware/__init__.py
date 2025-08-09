"""Middleware package for the Vocelio API Gateway."""

from .auth import auth_middleware
from .rate_limiting import rate_limit_middleware
try:
    from .logging import request_logging_middleware  # noqa
except Exception:  # pragma: no cover - fallback if file missing
    request_logging_middleware = None  # type: ignore

__all__ = [
    "auth_middleware",
    "rate_limit_middleware",
    "request_logging_middleware",
]
