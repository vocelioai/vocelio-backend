"""
AI Brain API Router - Main API endpoints
"""

from fastapi import APIRouter
from src.api.v1.endpoints import (
    generation,
    analysis, 
    sentiment,
    language,
    training,
    optimization,
    insights,
    neural_networks,
    predictions
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    generation.router, 
    prefix="/generation", 
    tags=["🤖 AI Generation"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    analysis.router, 
    prefix="/analysis", 
    tags=["📊 Text Analysis"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    sentiment.router, 
    prefix="/sentiment", 
    tags=["😊 Sentiment Analysis"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    language.router, 
    prefix="/language", 
    tags=["🌍 Language Processing"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    training.router, 
    prefix="/training", 
    tags=["🎓 Model Training"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    optimization.router, 
    prefix="/optimization", 
    tags=["⚡ AI Optimization"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    insights.router, 
    prefix="/insights", 
    tags=["💡 AI Insights"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    neural_networks.router, 
    prefix="/neural-networks", 
    tags=["🧠 Neural Networks"],
    responses={404: {"description": "Not found"}}
)

api_router.include_router(
    predictions.router, 
    prefix="/predictions", 
    tags=["🔮 Predictions"],
    responses={404: {"description": "Not found"}}
)

@api_router.get("/", tags=["🏠 Root"])
async def ai_brain_info():
    """AI Brain service information"""
    return {
        "service": "ai-brain",
        "version": "1.0.0",
        "description": "🧠 Advanced AI Processing Engine",
        "endpoints": {
            "generation": "AI text and conversation generation",
            "analysis": "Advanced text and conversation analysis",
            "sentiment": "Real-time sentiment analysis",
            "language": "Language detection and processing",
            "training": "Model training and fine-tuning",
            "optimization": "AI performance optimization",
            "insights": "Live AI insights and recommendations",
            "neural-networks": "Neural network management",
            "predictions": "AI predictions and forecasting"
        },
        "capabilities": [
            "Real-time conversation optimization",
            "Advanced sentiment analysis",
            "Predictive analytics",
            "Neural network management", 
            "Continuous learning",
            "Performance optimization",
            "Multi-language support",
            "Custom model training"
        ]
    }
