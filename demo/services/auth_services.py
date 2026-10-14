from sqlalchemy.orm import Session
from sqlalchemy import select
from demo.schemas.admin_schema import AdminCreate, AdminLogin, AdminResponse, AdminLoginResponse
from demo.models.admin import Admin
from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from demo.db.database import get_session
from uuid import UUID

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY').strip()

def create_access_token(admin: Admin) -> str:
    token = jwt.encode(
        {
            "sub": str(admin.uuid), 
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        SECRET_KEY, algorithm="HS256"
    )
    return token

#Reads token from the http header and let's the function below handle missing token.
bearer_scheme = HTTPBearer(auto_error=False)

def verify_access_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session)
) -> None:

    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )

    #If no token was sent:
    if credentials is None:
        raise unauthorized

    #jwt.decode checks if signature computed with SECRET_KEY matches with the one in the token,
    #and if the token is expired.
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        #if decode works, the token is valid. 
        #get the id of the admin it belongs to.
        admin_uuid = UUID(payload["sub"])
    except(jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized

    #check if an admin has been deleted from db since the token was created:
    admin = session.get(Admin, admin_uuid)
    if admin is None:
        raise unauthorized
    

#argon2 hash
password_hasher = PasswordHash.recommended()

def verify_login_details(session: Session, login_details: AdminLogin) -> Admin | None:
    admin = session.scalars(
        select(
            Admin
        ).where(
            Admin.username==login_details.username
        )
    ).first()

    #1. checks if username exists
    #2. hashes the entered password and compares it with the stored hash.
    if admin is None or (not password_hasher.verify(login_details.password, admin.password_hash)):
        return None
    return admin

