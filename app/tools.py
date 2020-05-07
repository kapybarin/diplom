from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
import datetime
from datetime import timedelta
from os import getenv
import jwt

from typing import Tuple

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = getenv("API_SECRET")
ALGORITHM = "HS512"


def is_valid_email(email: str) -> Tuple[bool, str]:
    try:
        valid = validate_email(email)
    except EmailNotValidError as e:
        return False, str(e)

    return True, str(valid.email)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
