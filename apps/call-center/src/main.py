# apps/call-center/src/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
import uvicorn

from api.v1.api import api_router
from core.config import settings
from shared.database.client import get_database
from shared.auth.dependencies import get_current_user
from shared.middleware.request_logging import RequestLoggingMiddleware
from shared.middleware.error_handling import ErrorHandlingMiddleware
from services.call_service import CallService
from services.webhook_service import WebhookService
from services.recording_service import RecordingService
from schemas.call import CallResponse, CallStatusUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio Call Center Service",
    description="Real-time AI Call Center monitoring and management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user's connections"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

# WebSocket endpoint for real-time call monitoring
@app.websocket("/ws/call-monitoring/{user_id}")
async def websocket_call_monitoring(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    call_service = CallService()
    
    try:
        while True:
            # Send real-time metrics every 2 seconds
            metrics = await call_service.get_live_metrics()
            active_calls = await call_service.get_active_calls(limit=50)
            
            update_data = {
                "type": "metrics_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "metrics": metrics,
                    "active_calls": [call.dict() for call in active_calls]
                }
            }
            
            await manager.send_personal_message(update_data, user_id)
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"User {user_id} disconnected from call monitoring")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, user_id)

# Global WebSocket for system broadcasts
@app.websocket("/ws/global")
async def websocket_global(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background task for broadcasting system updates
async def broadcast_system_updates():
    """Background task to broadcast system-wide updates"""
    call_service = CallService()
    
    while True:
        try:
            # Get global system metrics
            system_metrics = await call_service.get_system_health()
            
            broadcast_data = {
                "type": "system_update",
                "timestamp": datetime.utcnow().isoformat(),
                "data": system_metrics
            }
            
            await manager.broadcast(broadcast_data)
            await asyncio.sleep(10)  # Broadcast every 10 seconds
            
        except Exception as e:
            logger.error(f"Error in broadcast_system_updates: {e}")
            await asyncio.sleep(10)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "call-center",
        "timestamp": datetime.utcnow().isoformat(),
        "active_connections": len(manager.active_connections)
    }

# Service status endpoint
@app.get("/status")
async def service_status():
    call_service = CallService()
    system_health = await call_service.get_system_health()
    
    return {
        "service": "call-center",
        "version": "1.0.0",
        "status": "operational",
        "system_health": system_health,
        "active_websocket_connections": len(manager.active_connections),
        "timestamp": datetime.utcnow().isoformat()
    }

# Event handlers
@app.on_event("startup")
async def startup_event():
    logger.info("Call Center Service starting up...")
    
    # Start background tasks
    asyncio.create_task(broadcast_system_updates())
    
    logger.info("Call Center Service startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Call Center Service shutting down...")
    
    # Close all WebSocket connections
    for connection in manager.active_connections:
        try:
            await connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
    
    logger.info("Call Center Service shutdown complete")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,  # Call Center service port
        reload=True,
        log_level="info"
    )