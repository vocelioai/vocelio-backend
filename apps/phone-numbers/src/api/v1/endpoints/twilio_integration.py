# apps/phone-numbers/src/api/v1/endpoints/twilio_integration.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

router = APIRouter()

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "demo_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "demo_auth_token") 
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"

@router.get("/twilio/available-phone-numbers/{country_code}/{type}")
async def get_available_phone_numbers(
    country_code: str,
    type: str,
    area_code: Optional[str] = Query(None),
    contains: Optional[str] = Query(None),
    page_size: int = Query(20, le=1000)
):
    """
    Get available phone numbers from Twilio
    
    Args:
        country_code: Country code (e.g., US, CA, GB)
        type: Number type (Local, TollFree, Mobile)
        area_code: Optional area code filter
        contains: Optional pattern to search for in numbers
        page_size: Number of results to return (max 1000)
    """
    try:
        logger.info(f"🔍 Searching for {type} numbers in {country_code}")
        
        # In demo mode, return mock data
        if TWILIO_ACCOUNT_SID == "demo_account_sid":
            logger.info("📱 Using demo Twilio data")
            return {
                "available_phone_numbers": [
                    {
                        "phone_number": "+1234567890",
                        "friendly_name": "(123) 456-7890",
                        "iso_country": country_code,
                        "address_requirements": "none",
                        "beta": False,
                        "capabilities": {
                            "voice": True,
                            "sms": True,
                            "mms": True,
                            "fax": False
                        },
                        "locality": "San Francisco" if area_code == "415" else "New York",
                        "postal_code": "94102" if area_code == "415" else "10001",
                        "rate_center": "SNFC ZONE 1" if area_code == "415" else "NEW YORK ZONE 1",
                        "region": "CA" if area_code == "415" else "NY",
                        "lata": "722" if area_code == "415" else "132"
                    },
                    {
                        "phone_number": "+1234567891",
                        "friendly_name": "(123) 456-7891",
                        "iso_country": country_code,
                        "address_requirements": "none",
                        "beta": False,
                        "capabilities": {
                            "voice": True,
                            "sms": True,
                            "mms": True,
                            "fax": False
                        },
                        "locality": "San Francisco" if area_code == "415" else "New York",
                        "postal_code": "94102" if area_code == "415" else "10001",
                        "rate_center": "SNFC ZONE 1" if area_code == "415" else "NEW YORK ZONE 1",
                        "region": "CA" if area_code == "415" else "NY",
                        "lata": "722" if area_code == "415" else "132"
                    },
                    {
                        "phone_number": "+1234567892",
                        "friendly_name": "(123) 456-7892",
                        "iso_country": country_code,
                        "address_requirements": "none",
                        "beta": False,
                        "capabilities": {
                            "voice": True,
                            "sms": True,
                            "mms": True,
                            "fax": False
                        },
                        "locality": "San Francisco" if area_code == "415" else "New York",
                        "postal_code": "94102" if area_code == "415" else "10001",
                        "rate_center": "SNFC ZONE 1" if area_code == "415" else "NEW YORK ZONE 1",
                        "region": "CA" if area_code == "415" else "NY",
                        "lata": "722" if area_code == "415" else "132"
                    }
                ],
                "page": 0,
                "page_size": page_size,
                "next_page_uri": None,
                "previous_page_uri": None,
                "uri": f"/AvailablePhoneNumbers/{country_code}/{type}.json"
            }
        
        # Real Twilio API call
        params: Dict[str, Any] = {
            "PageSize": page_size
        }
        
        if area_code:
            params["AreaCode"] = area_code
            
        if contains:
            params["Contains"] = contains
        
        # Construct Twilio API URL
        url = f"{TWILIO_API_BASE}/Accounts/{TWILIO_ACCOUNT_SID}/AvailablePhoneNumbers/{country_code}/{type}.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully fetched {country_code} {type} numbers")
                return response.json()
            else:
                logger.error(f"❌ Twilio API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "Twilio API error",
                        "message": response.text,
                        "status_code": response.status_code
                    }
                )
                
    except httpx.TimeoutException:
        logger.error("⏰ Timeout calling Twilio API")
        raise HTTPException(
            status_code=504,
            detail={
                "error": "Twilio API timeout",
                "message": "The Twilio service took too long to respond. Please try again."
            }
        )
    except Exception as e:
        logger.error(f"💥 Error fetching available phone numbers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to fetch available phone numbers"
            }
        )

@router.post("/twilio/incoming-phone-numbers")
async def purchase_phone_number(phone_number: str, webhook_url: Optional[str] = None):
    """
    Purchase a phone number from Twilio
    
    Args:
        phone_number: The phone number to purchase (e.g., +15551234567)
        webhook_url: Optional webhook URL for incoming calls
    """
    try:
        logger.info(f"💳 Purchasing phone number: {phone_number}")
        
        # In demo mode, return mock data
        if TWILIO_ACCOUNT_SID == "demo_account_sid":
            logger.info("📱 Using demo Twilio purchase")
            return {
                "account_sid": TWILIO_ACCOUNT_SID,
                "sid": f"PN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}demo",
                "phone_number": phone_number,
                "friendly_name": phone_number,
                "status": "in-use",
                "capabilities": {
                    "voice": True,
                    "sms": True,
                    "mms": True,
                    "fax": False
                },
                "voice_url": webhook_url or "",
                "voice_method": "POST",
                "sms_url": webhook_url or "",
                "sms_method": "POST",
                "date_created": datetime.utcnow().isoformat(),
                "date_updated": datetime.utcnow().isoformat(),
                "api_version": "2010-04-01"
            }
        
        # Real Twilio API call
        url = f"{TWILIO_API_BASE}/Accounts/{TWILIO_ACCOUNT_SID}/IncomingPhoneNumbers.json"
        
        data = {
            "PhoneNumber": phone_number
        }
        
        if webhook_url:
            data["VoiceUrl"] = webhook_url
            data["SmsUrl"] = webhook_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=data,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30.0
            )
            
            if response.status_code == 201:
                logger.info(f"✅ Successfully purchased phone number: {phone_number}")
                return response.json()
            else:
                logger.error(f"❌ Twilio purchase error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "Failed to purchase phone number",
                        "message": response.text,
                        "status_code": response.status_code
                    }
                )
                
    except Exception as e:
        logger.error(f"💥 Error purchasing phone number: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to purchase phone number"
            }
        )

@router.get("/twilio/incoming-phone-numbers")
async def list_phone_numbers():
    """List all purchased phone numbers"""
    try:
        logger.info("📋 Listing purchased phone numbers")
        
        # In demo mode, return mock data
        if TWILIO_ACCOUNT_SID == "demo_account_sid":
            return {
                "incoming_phone_numbers": [
                    {
                        "account_sid": TWILIO_ACCOUNT_SID,
                        "sid": "PN123456789demo1",
                        "phone_number": "+15551234567",
                        "friendly_name": "+15551234567",
                        "status": "in-use",
                        "capabilities": {
                            "voice": True,
                            "sms": True,
                            "mms": True,
                            "fax": False
                        },
                        "voice_url": "",
                        "sms_url": "",
                        "date_created": "2024-01-01T00:00:00Z",
                        "date_updated": "2024-01-01T00:00:00Z"
                    },
                    {
                        "account_sid": TWILIO_ACCOUNT_SID,
                        "sid": "PN123456789demo2",
                        "phone_number": "+15551234568",
                        "friendly_name": "+15551234568",
                        "status": "in-use",
                        "capabilities": {
                            "voice": True,
                            "sms": True,
                            "mms": True,
                            "fax": False
                        },
                        "voice_url": "",
                        "sms_url": "",
                        "date_created": "2024-01-01T00:00:00Z",
                        "date_updated": "2024-01-01T00:00:00Z"
                    }
                ],
                "page": 0,
                "page_size": 50,
                "next_page_uri": None,
                "previous_page_uri": None
            }
        
        # Real Twilio API call
        url = f"{TWILIO_API_BASE}/Accounts/{TWILIO_ACCOUNT_SID}/IncomingPhoneNumbers.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully listed phone numbers")
                return response.json()
            else:
                logger.error(f"❌ Twilio API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "Twilio API error",
                        "message": response.text
                    }
                )
                
    except Exception as e:
        logger.error(f"💥 Error listing phone numbers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to list phone numbers"
            }
        )

@router.delete("/twilio/incoming-phone-numbers/{phone_number_sid}")
async def release_phone_number(phone_number_sid: str):
    """Release a phone number"""
    try:
        logger.info(f"🗑️ Releasing phone number: {phone_number_sid}")
        
        # In demo mode, return success
        if TWILIO_ACCOUNT_SID == "demo_account_sid":
            return {
                "message": "Phone number released successfully",
                "sid": phone_number_sid,
                "status": "released"
            }
        
        # Real Twilio API call
        url = f"{TWILIO_API_BASE}/Accounts/{TWILIO_ACCOUNT_SID}/IncomingPhoneNumbers/{phone_number_sid}.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30.0
            )
            
            if response.status_code == 204:
                logger.info(f"✅ Successfully released phone number: {phone_number_sid}")
                return {
                    "message": "Phone number released successfully",
                    "sid": phone_number_sid,
                    "status": "released"
                }
            else:
                logger.error(f"❌ Twilio release error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "Failed to release phone number",
                        "message": response.text
                    }
                )
                
    except Exception as e:
        logger.error(f"💥 Error releasing phone number: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to release phone number"
            }
        )

@router.get("/twilio/accounts/{account_sid}")
async def get_account_info(account_sid: str):
    """Get Twilio account information"""
    try:
        logger.info(f"📊 Getting account info for: {account_sid}")
        
        # In demo mode, return mock data
        if TWILIO_ACCOUNT_SID == "demo_account_sid":
            return {
                "sid": account_sid,
                "friendly_name": "Vocelio.ai Demo Account",
                "status": "active",
                "type": "Full",
                "date_created": "2024-01-01T00:00:00Z",
                "date_updated": "2024-01-01T00:00:00Z",
                "auth_token": "hidden",
                "uri": f"/Accounts/{account_sid}.json"
            }
        
        # Real Twilio API call
        url = f"{TWILIO_API_BASE}/Accounts/{account_sid}.json"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
                timeout=30.0
            )
            
            if response.status_code == 200:
                logger.info("✅ Successfully fetched account info")
                return response.json()
            else:
                logger.error(f"❌ Twilio API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail={
                        "error": "Twilio API error",
                        "message": response.text
                    }
                )
                
    except Exception as e:
        logger.error(f"💥 Error fetching account info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": "Failed to fetch account information"
            }
        )
