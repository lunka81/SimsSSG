import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from demo.routes.camera_routes import camera_router
from demo.routes.employee_routes import employee_router

load_dotenv()
app = FastAPI(debug=os.getenv("DEBUG", "False").lower() == "true")
app.include_router(camera_router)
app.include_router(employee_router)


# React kör på port 5173 och FastAPI på en annan port.
# Webbläsaren betraktar dem därför som olika origins och kräver
# att backend uttryckligen tillåter anrop från React-adressen.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
