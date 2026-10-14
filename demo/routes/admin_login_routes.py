from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from demo.db.database import get_session
from demo.schemas.admin_schema import AdminResponse, AdminLoginResponse, AdminCreate, AdminLogin
from demo.services.admin_services import add_admin, username_unique
from demo.services.auth_services import create_access_token, verify_login_details, verify_access_token
login_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@login_router.post("/login", response_model=AdminLoginResponse)
def authorize_login(login_details: AdminLogin, session: Session = Depends(get_session)) -> AdminLoginResponse:
    #HTTP status code communicates approved or denied login attempt:
    #200 -> authorized
    #401 -> unauthorized
    admin = verify_login_details(session, login_details)
    if admin is None:
        raise HTTPException(
            status_code=401,
            detail="Wrong password or username."
        )
    return AdminLoginResponse( #status code 200
        username=admin.username,
        uuid=admin.uuid,
        access_token=create_access_token(admin)
    )
    
@login_router.post("/register", response_model=AdminResponse)
def register_admin(admin: AdminCreate, session: Session = Depends(get_session)) -> AdminResponse:
    if not username_unique(session, admin.username):
        raise HTTPException(
            status_code=409,
            detail="Username already taken."
        ) 
    new_admin = add_admin(session, admin)
    return new_admin