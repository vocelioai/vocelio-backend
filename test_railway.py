#!/usr/bin/env python3
"""
Simple Railway deployment test
Check if we can start the most basic FastAPI app
"""

from fastapi import FastAPI
import uvicorn
import os

app = FastAPI(
    title="Vocelio Test",
    description="Simple test to verify Railway deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vocelio Backend is running!",
        "port": os.environ.get("PORT", "unknown"),
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "unknown"),
        "service": "test-deployment"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "vocelio-test"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
