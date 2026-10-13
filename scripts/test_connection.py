import requests

from config.config import BACKEND_URL, DEVICE_API_KEY, SERVER_TIMEOUT

try:
    response = requests.get(
        f"{BACKEND_URL}/device/ping",
        headers={
            "X-API-Key": DEVICE_API_KEY
        },
        timeout=SERVER_TIMEOUT
    )

    print("HTTP-status:", response.status_code)
    print("Svar:", response.text)
    response.raise_for_status()

except requests.RequestException as error:
    print("Anropet misslyckades:", error)
