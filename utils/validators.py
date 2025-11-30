import re

EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"
PHONE_PATTERN = r"^[0-9\-\+\(\) ]{7,15}$"

def is_email(x: str):
    if x is None:
        return False
    return re.match(EMAIL_PATTERN, str(x)) is not None

def is_phone(x: str):
    if x is None:
        return False
    return re.match(PHONE_PATTERN, str(x)) is not None
