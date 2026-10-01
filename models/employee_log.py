from db.database import Base
from models.employee import Employee


class EmployeeLog(Base):
    __tablename__ = "employee_log"
