#!/usr/bin/env python3
"""
📞 Vocelio.ai Phone Numbers Service - Test Version
Simplified version for testing without Twilio/Stripe dependencies
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import uvicorn

# Pydantic Models
class PhoneNumber(BaseModel):
    """Phone number model"""
    phone_number: str = Field(..., description="Phone number in E.164 format")
    country_code: str = Field(..., description="Country code")
    area_code: str = Field(..., description="Area code")
    type: str = Field(..., description="Number type (local, toll-free, mobile)")
    status: str = Field(..., description="Number status")
    monthly_cost: float = Field(..., description="Monthly cost in USD")
    capabilities: List[str] = Field(..., description="Number capabilities")
    assigned_to: Optional[str] = Field(None, description="Assigned to client")
    created_at: datetime = Field(default_factory=datetime.now)

class PhoneNumberPurchase(BaseModel):
    """Phone number purchase request"""
    country: str = Field(..., description="Country for phone number")
    area_code: Optional[str] = Field(None, description="Preferred area code")
    type: str = Field("local", description="Number type preference")
    capabilities: List[str] = Field(["voice", "sms"], description="Required capabilities")

class PhoneNumberStats(BaseModel):
    """Phone number statistics"""
    total_numbers: int = Field(..., description="Total phone numbers")
    active_numbers: int = Field(..., description="Active phone numbers")
    available_numbers: int = Field(..., description="Available phone numbers")
    monthly_cost: float = Field(..., description="Total monthly cost")
    countries: int = Field(..., description="Number of countries")
    usage_today: int = Field(..., description="Usage today")

# FastAPI app
app = FastAPI(
    title="📞 Vocelio.ai Phone Numbers Service (Test)",
    description="Global phone number management with Twilio integration - Test Version",
    version="1.0.0-test"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
MOCK_PHONE_NUMBERS = [
    {
        "phone_number": "+1234567890",
        "country_code": "US",
        "area_code": "234",
        "type": "local",
        "status": "active",
        "monthly_cost": 1.50,
        "capabilities": ["voice", "sms"],
        "assigned_to": "client_001",
        "created_at": datetime.now()
    },
    {
        "phone_number": "+447700900123",
        "country_code": "GB",
        "area_code": "770",
        "type": "local",
        "status": "active",
        "monthly_cost": 2.00,
        "capabilities": ["voice", "sms"],
        "assigned_to": "client_002",
        "created_at": datetime.now()
    },
    {
        "phone_number": "+33123456789",
        "country_code": "FR",
        "area_code": "123",
        "type": "toll-free",
        "status": "available",
        "monthly_cost": 3.50,
        "capabilities": ["voice", "sms", "mms"],
        "assigned_to": None,
        "created_at": datetime.now()
    }
]

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vocelio.ai Phone Numbers Service",
        "version": "1.0.0-test",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "service": "phone-numbers",
        "status": "healthy",
        "version": "1.0.0-test",
        "timestamp": datetime.now().isoformat(),
        "twilio_connected": True,  # Mock
        "stripe_connected": True   # Mock
    }

@app.get("/api/v1/phone-numbers", response_model=List[PhoneNumber])
async def get_phone_numbers(
    country: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None
):
    """Get all phone numbers with optional filtering"""
    numbers = MOCK_PHONE_NUMBERS.copy()
    
    if country:
        numbers = [n for n in numbers if n["country_code"] == country.upper()]
    if status:
        numbers = [n for n in numbers if n["status"] == status]
    if type:
        numbers = [n for n in numbers if n["type"] == type]
    
    return numbers

@app.get("/api/v1/phone-numbers/{phone_number}")
async def get_phone_number(phone_number: str):
    """Get specific phone number details"""
    for number in MOCK_PHONE_NUMBERS:
        if number["phone_number"] == phone_number:
            return number
    
    raise HTTPException(status_code=404, detail="Phone number not found")

@app.post("/api/v1/phone-numbers/purchase", response_model=PhoneNumber)
async def purchase_phone_number(purchase_request: PhoneNumberPurchase):
    """Purchase a new phone number"""
    # Generate mock phone number
    new_number = {
        "phone_number": f"+{random.randint(1000000000, 9999999999)}",
        "country_code": purchase_request.country.upper(),
        "area_code": purchase_request.area_code or f"{random.randint(100, 999)}",
        "type": purchase_request.type,
        "status": "active",
        "monthly_cost": round(random.uniform(1.0, 5.0), 2),
        "capabilities": purchase_request.capabilities,
        "assigned_to": None,
        "created_at": datetime.now()
    }
    
    MOCK_PHONE_NUMBERS.append(new_number)
    return new_number

@app.delete("/api/v1/phone-numbers/{phone_number}")
async def release_phone_number(phone_number: str):
    """Release a phone number"""
    for i, number in enumerate(MOCK_PHONE_NUMBERS):
        if number["phone_number"] == phone_number:
            MOCK_PHONE_NUMBERS.pop(i)
            return {"message": f"Phone number {phone_number} released successfully"}
    
    raise HTTPException(status_code=404, detail="Phone number not found")

@app.get("/api/v1/stats", response_model=PhoneNumberStats)
async def get_phone_number_stats():
    """Get phone number statistics"""
    active_numbers = [n for n in MOCK_PHONE_NUMBERS if n["status"] == "active"]
    available_numbers = [n for n in MOCK_PHONE_NUMBERS if n["status"] == "available"]
    total_cost = sum(n["monthly_cost"] for n in MOCK_PHONE_NUMBERS)
    countries = len(set(n["country_code"] for n in MOCK_PHONE_NUMBERS))
    
    return PhoneNumberStats(
        total_numbers=len(MOCK_PHONE_NUMBERS),
        active_numbers=len(active_numbers),
        available_numbers=len(available_numbers),
        monthly_cost=total_cost,
        countries=countries,
        usage_today=random.randint(50, 200)
    )

@app.get("/api/v1/countries")
async def get_available_countries():
    """Get list of countries with available phone numbers"""
    return {
        "countries": [
            {"code": "US", "name": "United States", "available": True},
            {"code": "GB", "name": "United Kingdom", "available": True},
            {"code": "FR", "name": "France", "available": True},
            {"code": "DE", "name": "Germany", "available": True},
            {"code": "CA", "name": "Canada", "available": True},
            {"code": "AU", "name": "Australia", "available": True},
        ]
    }

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
