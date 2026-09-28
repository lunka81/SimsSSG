from fastapi import FastAPI, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from Database.database import engine, SessionLocal, Base
from Models.demo_model import Employee

from pydantic import BaseModel

# Create tables for all imported models (only creates missing tables)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return employees

class EmployeeCreate(BaseModel):
    name: str


@app.post("/employees")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_emp = Employee(name = employee.name)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp