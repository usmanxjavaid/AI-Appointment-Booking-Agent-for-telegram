import re
from core.logger import logger
from datetime import datetime, timedelta
from config import Config

def validate_name(name: str) -> bool:
    """
    Valid: John smith, Michael anderson, Maria
    Invalid: 123, empty, @@@
    """
    name = name.strip()
    if len(name) < 2:
        logger.warning(f"Invalid name: {name}")
        return False
    
    pattern = r"^[\w\s\-\'\.]+$"
    is_valid = bool(re.match(pattern, name, re.UNICODE))
    if not is_valid:
        logger.warning(f"Invalid name: {name}")
    return is_valid


def validate_phone(phone: str) -> bool:
    """
    Accepts international phone numbers.
    Valid: +1-800-555-0199, +44 7911 123456
    Invalid: 1234, abcd, 8938e
    """
    cleaned = re.sub(r'[\s\-\(\)\\.]', '', phone.strip())
    if cleaned.startswith('+'):
        digits = cleaned[1:]
    else:
        digits = cleaned

    if not digits.isdigit():
        logger.warning(f"Invalid phone number: {phone}")
        return False
    is_valid = 7 <= len(digits) <= 15
    if not is_valid:
        logger.warning(f"Invalid phone number: {phone}")
    return is_valid

def get_available_dates() -> list:
    """
    Returns next 3 working days from today.
    skips sunday automatically.
    """
    dates = []
    current = datetime.now()
    days_checked = 0

    while len(dates) < 3:
        days_checked += 1
        next_day = current + timedelta(days=days_checked)
        day_name = next_day.strftime('%A') # Monday, Tuesday

        if day_name in Config.WORKING_DAYS:
            dates.append({
                "display": next_day.strftime("%A, %d %B"), # display: "Monday, 27 January"
                "value": next_day.strftime("%Y-%m-%d") # "value": "2036-01-27"
            })
    return dates
