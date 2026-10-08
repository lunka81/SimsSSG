import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

url = os.environ["BACKEND_URL"].rstrip("/")

try:
    response = httpx.get(
        f"{url}/device/ping",
        headers={
            "X-API-Key": os.environ["DEVICE_API_KEY"]
        },
        timeout=5
    )

    print("HTTP-status:", response.status_code)
    print("Svar:", response.text)
    response.raise_for_status()

except httpx.HTTPError as error:
    print("Anropet misslyckades:", error)