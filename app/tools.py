from email_validator import validate_email, EmailNotValidError

from typing import Tuple


def is_valid_email(email:str) -> Tuple[bool, str]:
    try:
        valid = validate_email(email)
        return True, email
    except EmailNotValidError as e:
        return False, str(e)