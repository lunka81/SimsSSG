from sqlalchemy.orm import Session
from sqlalchemy import select
from demo.schemas.admin_schema import AdminCreate, AdminLogin, AdminResponse, AdminLoginResponse
from demo.services.employee_services import build_employee
from demo.models.admin import Admin
from demo.models.employee_test import Permission

#argon2 hash
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()
#perhaps add functionality to promote an employee to admin (without creating a new employee entity)

def username_unique(session: Session, username: str) -> bool:
    admin = session.scalars(
            select(
                Admin
            ).where(
                Admin.username==username
            )
        ).first()
    return True if admin is None else False

def add_admin(session: Session, admin: AdminCreate) -> AdminResponse:
    #since AdminCreate inherits from EmployeeCreate, 
    #you can simple pass in an child instance where a base instance is expected,
    #and the extra member variables in AdminCreate are ignored.
    emp = build_employee(admin)
    #One could create an admin with another employee permission value without this.
    emp.permission = Permission.ADMIN
    password_hash = password_hasher.hash(admin.plain_password)
    emp.admin = Admin(
        username=admin.username, 
        password_hash=password_hash, 
    )
    #create the relation between the new employee and their admin account.
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return AdminResponse(
        username=emp.admin.username,
        uuid=emp.admin.uuid
    )

