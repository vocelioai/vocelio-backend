"""Vocelio API Gateway package initializer.

Ensures Python treats the `src` directory as a package so that
relative imports like `from .middleware.auth import auth_middleware`
work correctly when running the gateway with `python -m src.main`.
"""

__all__ = ["main"]
