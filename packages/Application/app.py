from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from Database.database import engine, SessionLocal, Base
from Models.demo_model import Employee

import base64
from pydantic import BaseModel, ConfigDict, Field, Base64Bytes, field_serializer

from datetime import datetime

# Create tables for all imported models (only creates missing tables)
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware( #FastAPI and react run on different ports
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()

    try:
        yield db #yield gör funktionen till en generator.
        #koden körs fram till yield, och pausar där.
    finally: #när anroparen är klar, körs blocket nedan.
        #finally: koden körs även om det blev nån error i endpoint:en
        db.close()


class EmployeeOut(BaseModel): 
    model_config = ConfigDict(from_attributes=True)  # lets pydantic read SQLAlchemy objects
    id: int
    name: str
    approved: bool
    logs: list[str]
    timestamp: datetime

class EmployeeOutWithPic(EmployeeOut):

    picture: bytes
    @field_serializer("picture")
    def encode_picture(self, v: bytes) -> str:
        return base64.b64encode(v).decode() #encode ger ett bytes-objekt, decode gör om det till str.

class EmployeeCreate(BaseModel): #Så att fastAPI vet att det är json inkommande
    name: str
    picture: Base64Bytes                    # client sends base64 text, you get bytes
    embedding: list[float] = Field(min_length=512, max_length=512)
    approved: bool = False
    logs: list[str] = []

    

#olika attribut accepteras på vägen in och på vägen ut.
#om svaret innehåller bild och embedding försöker FastAPI översätta det till json och kraschar. 
#dessa värden läggs till i databasen men inkluderas inte i http-response. 

@app.get("/employees", response_model=list[EmployeeOut])
#En session per requst
#FastAPI anropar get_db, som ber om en db-session, som tilldelas till db inom funktionens scope.
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return employees

@app.get("/employees/{emp_id}", response_model=EmployeeOutWithPic)
def get_employee_with_pic(emp_id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return emp

@app.post("/employees", response_model=EmployeeOut)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_emp = Employee(
        name = employee.name,
        picture = employee.picture,
        embedding = employee.embedding,
        approved = employee.approved,
        logs = employee.logs,
        timestamp = datetime.now()    
    )
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

#empty response body
@app.delete("/employees", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(emp_id : int, db : Session = Depends(get_db)):
    emp = db.get(Employee, emp_id) 
    if emp is None: #if id isn't found cached or in db
        raise HTTPException(status_code=404, detail="Employee not found.")

    db.delete(emp)
    db.commit()


