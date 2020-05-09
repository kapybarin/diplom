from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pony.orm import db_session
from os import getenv
import jwt

from typing import Tuple
from models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = getenv("API_SECRET", 'aaef2e5483cc355ddb517e1696539d0276667b93cd711ff20138f94809e2a8eb')
ALGORITHM = 'HS256'


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


@db_session
def validate_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return False, None
    except jwt.PyJWTError:
        return False, None
    user = User.get(email=email)
    if user is None:
        return False, None
    return True, email
