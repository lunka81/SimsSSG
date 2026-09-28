from fastapi import FastAPI, Depends
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from Database.database import engine, SessionLocal, Base
from Models.demo_model import Employee

from pydantic import BaseModel, ConfigDict, Field, Base64Bytes

from datetime import datetime

# Create tables for all imported models (only creates missing tables)
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()

    try:
        yield db #yield gör funktionen till en generator.
        #koden körs fram till yield, och pausar där.
    finally: #när anroparen är klar, körs blocket nedan.
        #finally: koden körs även om det blev nån error i endpoint:en
        db.close()



@app.get("/employees")
#En session per requst
#FastAPI anropar get_db, som ber om en db-session, som tilldelas till var db inom funktionens scope.
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return employees

class EmployeeCreate(BaseModel): #Så att fastAPI förväntar sig json.
    name: str
    picture: Base64Bytes                    # client sends base64 text, you get bytes
    embedding: list[float] = Field(min_length=512, max_length=512)
    approved: bool = False
    logs: list[str] = []

#olika attribut accepteras på vägen in och på vägen ut.
#om svaret innehåller bild och embedding försöker FastAPI översätta det till json och kraschar. 
#dessa värden läggs till i databasen men inkluderas inte i http-response. 
class EmployeeOut(BaseModel): 
    model_config = ConfigDict(from_attributes=True)  # lets pydantic read SQLAlchemy objects
    id: int
    name: str
    approved: bool
    logs: list[str]
    timestamp: datetime


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

'''@app.post("/hello/{user}")
def greet(user: str):
    return{
        "message": f"Hello {user}"
    }
'''
