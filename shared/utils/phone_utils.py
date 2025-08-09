# shared/utils/phone_utils.py
import re
from typing import Optional, Dict, Any
import phonenumbers
from phonenumbers import geocoder, carrier, timezone


def normalize_phone_number(phone_number: str) -> str:
    """Normalize phone number to E.164 format"""
    try:
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        
        # Add + if not present
        if not cleaned.startswith('+'):
            # Assume US/CA if no country code
            if len(cleaned) == 10:
                cleaned = '+1' + cleaned
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                cleaned = '+' + cleaned
            else:
                cleaned = '+' + cleaned
        
        # Parse and format using phonenumbers library
        parsed = phonenumbers.parse(cleaned, None)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        
    except phonenumbers.NumberParseException:
        # If parsing fails, return cleaned version
        return cleaned


def validate_phone_number(phone_number: str, expected_country: Optional[str] = None) -> bool:
    """Validate phone number format and country"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        # Check if number is valid
        if not phonenumbers.is_valid_number(parsed):
            return False
        
        # Check country if specified
        if expected_country:
            number_country = phonenumbers.region_code_for_number(parsed)
            if number_country != expected_country:
                return False
        
        return True
        
    except phonenumbers.NumberParseException:
        return False


def format_phone_number(phone_number: str, format_type: str = "international") -> str:
    """Format phone number for display"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        if format_type == "international":
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        elif format_type == "national":
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        elif format_type == "e164":
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        else:
            return normalized
            
    except phonenumbers.NumberParseException:
        return phone_number


def get_phone_number_info(phone_number: str) -> Dict[str, Any]:
    """Get detailed information about a phone number"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        info = {
            "normalized": normalized,
            "formatted_international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "formatted_national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            "country_code": phonenumbers.region_code_for_number(parsed),
            "country_calling_code": parsed.country_code,
            "national_number": parsed.national_number,
            "is_valid": phonenumbers.is_valid_number(parsed),
            "is_possible": phonenumbers.is_possible_number(parsed),
            "number_type": phonenumbers.number_type(parsed).name if phonenumbers.is_valid_number(parsed) else None,
            "location": geocoder.description_for_number(parsed, "en") or None,
            "carrier": carrier.name_for_number(parsed, "en") or None,
            "timezones": timezone.time_zones_for_number(parsed) or []
        }
        
        return info
        
    except phonenumbers.NumberParseException as e:
        return {
            "normalized": phone_number,
            "error": str(e),
            "is_valid": False
        }


def detect_number_type(phone_number: str) -> str:
    """Detect number type (local, toll_free, mobile)"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        if not phonenumbers.is_valid_number(parsed):
            return "unknown"
        
        number_type = phonenumbers.number_type(parsed)
        
        # Map phonenumbers types to our types
        type_mapping = {
            phonenumbers.PhoneNumberType.FIXED_LINE: "local",
            phonenumbers.PhoneNumberType.MOBILE: "mobile", 
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "local",
            phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "premium",
            phonenumbers.PhoneNumberType.SHARED_COST: "shared",
            phonenumbers.PhoneNumberType.VOIP: "voip",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "personal",
            phonenumbers.PhoneNumberType.PAGER: "pager",
            phonenumbers.PhoneNumberType.UAN: "uan",
            phonenumbers.PhoneNumberType.VOICEMAIL: "voicemail"
        }
        
        return type_mapping.get(number_type, "unknown")
        
    except phonenumbers.NumberParseException:
        return "unknown"


def extract_area_code(phone_number: str, country_code: str = "US") -> Optional[str]:
    """Extract area code from phone number"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        # For US/CA numbers, extract area code
        if phonenumbers.region_code_for_number(parsed) in ["US", "CA"]:
            national_str = str(parsed.national_number)
            if len(national_str) >= 10:
                return national_str[:3]
        
        return None
        
    except phonenumbers.NumberParseException:
        return None


def is_toll_free_number(phone_number: str) -> bool:
    """Check if number is toll-free"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        return phonenumbers.number_type(parsed) == phonenumbers.PhoneNumberType.TOLL_FREE
        
    except phonenumbers.NumberParseException:
        return False


def is_mobile_number(phone_number: str) -> bool:
    """Check if number is mobile"""
    try:
        normalized = normalize_phone_number(phone_number)
        parsed = phonenumbers.parse(normalized, None)
        
        number_type = phonenumbers.number_type(parsed)
        return number_type in [
            phonenumbers.PhoneNumberType.MOBILE,
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE
        ]
        
    except phonenumbers.NumberParseException:
        return False


def get_number_capabilities(phone_number: str, country_code: str) -> list:
    """Get expected capabilities for a phone number"""
    try:
        capabilities = ["voice"]  # All numbers support voice
        
        # Check if SMS is supported
        if not is_toll_free_number(phone_number):
            capabilities.append("sms")
        
        # Check if MMS is supported (usually mobile numbers)
        if is_mobile_number(phone_number):
            capabilities.append("mms")
        
        return capabilities
        
    except Exception:
        return ["voice"]  # Fallback to voice only


def format_number_for_display(phone_number: str, country_code: str = "US") -> str:
    """Format number for user-friendly display"""
    try:
        if country_code in ["US", "CA"]:
            # US/CA formatting: +1 (555) 123-4567
            normalized = normalize_phone_number(phone_number)
            if normalized.startswith("+1") and len(normalized) == 12:
                digits = normalized[2:]  # Remove +1
                return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        
        # For other countries, use international format
        return format_phone_number(phone_number, "international")
        
    except Exception:
        return phone_number