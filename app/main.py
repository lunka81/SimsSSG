import os
import secrets

from fastapi import Header, HTTPException
app = FastAPI()

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