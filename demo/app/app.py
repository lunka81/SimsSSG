import os
import secrets
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Header, HTTPException
from demo.routes.camera_routes import camera_router
from demo.routes.employee_routes import employee_router

load_dotenv()
app = FastAPI(debug=os.getenv("DEBUG", "False").lower() == "true")
app.include_router(camera_router)
app.include_router(employee_router)

'''
React kör på port 5173 och FastAPI på en annan port.
Webbläsaren betraktar dem därför som olika origins och kräver
att backend uttryckligen tillåter anrop från React-adressen.
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/device/ping")
def device_ping(
    x_api_key: str | None = Header(default=None)
):
    expected_key = os.environ["DEVICE_API_KEY"]

    if x_api_key is None or not secrets.compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return {"message": "Kontakt med backend fungerar"}


