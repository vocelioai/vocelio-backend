"""
📝 Request Logging Middleware for Vocelio Services
Logs all incoming requests for monitoring and debugging
"""

from fastapi import FastAPI, Request
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_requests(request: Request, call_next):
    """Middleware function to log all requests and responses"""
    # Start timing
    start_time = time.time()
    
    # Log request
    logger.info(f"📨 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.2f}s")
    
    return response

def add_request_logging(app: FastAPI) -> None:
    """Add request logging middleware to FastAPI app"""
    app.middleware("http")(log_requests)
    print("✅ Request logging middleware added")
