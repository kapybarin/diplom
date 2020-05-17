from email_validator import validate_email, EmailNotValidError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pony.orm import db_session, commit
from os import getenv
from fastapi import status
from random import randrange
import jwt

from typing import Tuple
from app.models import User, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = getenv(
    "API_SECRET", "aaef2e5483cc355ddb517e1696539d0276667b93cd711ff20138f94809e2a8eb"
)
ALGORITHM = "HS256"


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


def generate_token_value():
    return (str(randrange(0, 999999))).zfill(6)


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


@db_session
def get_user_by_token(token: str):
    is_valid_token, email = validate_token(token)
    if not is_valid_token:
        return None, {"err": "Token is not valid"}, status.HTTP_403_FORBIDDEN
    u = User.get(email=email)
    if not u:
        return (
            None,
            {"error": f"No user with email {email} found"},
            status.HTTP_404_NOT_FOUND,
        )
    return u, None, status.HTTP_200_OK


@db_session
def create_new_token(user_id: int, lease_id: int):
    while True:
        try:
            t = Token(
                user_id=user_id,
                expires_at=datetime.utcnow() + timedelta(days=30),
                lease_id=lease_id,
                value=generate_token_value(),
            )
            commit()
            break
        except:
            pass
    return t
