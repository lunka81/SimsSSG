from fastapi import APIRouter, Depends, HTTPException, Response, status, Header
from demo.schemas.comparison_schema import ComparisonRequest, ComparisonResponse
from demo.services import comparison_services
from sqlalchemy.orm import Session
from demo.db.database import get_session
from demo.schemas.admin_schema import AdminResponse, AdminLoginResponse
from demo.services.admin_services import verify_login_details
login_router = APIRouter(
    prefix="/auth",
    tags=["identify"]
)

@login_router.post("/login", response_model=AdminResponse)
#TODO: change password type to hash type later
def authorize_login(username: str, hashed_password: str) -> AdminLoginResponse:
    approved = verify_login_details(username, hashed_password)


@login_router.post("/register", response_model=AdminResponse)
#TODO: change password type to hash type later
def register_admin(username: str, hashed_password: str) -> AdminResponse:
    