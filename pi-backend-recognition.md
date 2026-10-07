# Receiving the Raspberry Pi's recognition request in the backend

In the new package, `main.py` starts [RecognitionService](raspberry-packages/services/recognition_service.py), which runs the camera loop in a background thread. Each time it sees a live face, it calls `recognize()` in [clients/uploader.py](raspberry-packages/clients/uploader.py), which POSTs to the backend. The backend's route has to match that request in every detail.

## What the Pi sends

| | Value |
|---|---|
| **URL** | `{BACKEND_URL}/recognition/identify`, built in [config.py:19](raspberry-packages/config/config.py#L19) |
| **Header** | `X-API-Key: <DEVICE_API_KEY>` |
| **Body** | `camera_id`, `timestamp`, `detection_confidence`, `face_width`, `face_height`, `embedding` (128 floats) |
| **Timeout** | 5 seconds |

`timestamp` is now an ISO string such as `"2026-10-07T12:00:00+00:00"`. The old `face_client.py` sent a Unix number. If the backend declares the field as `datetime`, Pydantic accepts both.

## What the Pi expects back

The service only acts on an answer that meets all of these ([recognition_service.py:249-282](raspberry-packages/services/recognition_service.py#L249-L282)):

- **Status 200.** Anything else counts as "no usable answer": nothing happens, and the service tries again about a second later.
- **A JSON object with `"approved"` set to `true` or `false`.** If `approved` is missing or isn't a boolean, the answer is thrown away.
- **Optionally `"name"`**, which gets printed on approval.

So a stranger has to get `200` with `{"approved": false}`. That's what makes the Pi call `lock.deny()`.

The Pi package already contains a matching contract in [schemas/recognition_schema.py](raspberry-packages/schemas/recognition_schema.py): `RecognitionRequest` and `RecognitionResponse(approved, employee_uuid, name)`. The backend should use those same two schemas.

## What doesn't match in the backend yet

1. **Wrong URL.** The backend's route is `POST /api/employee/recognize`, so the Pi's requests to `/recognition/identify` get a **404**. Either move the route, for example to a new router with `prefix="/recognition"` and `@router.post("/identify")`, or change `SERVER_URL` in the Pi's config.
2. **Wrong response field.** `ComparisonResponse` answers with `recognized`, but the service looks for `approved`, so it would discard every answer. Use the Pi's `RecognitionResponse` in place of `ComparisonResponse`. You can add `similarity: float | None = None` to it for debugging, since the Pi ignores extra fields.
3. **The route calls functions that don't exist.** `employee_services.find_nearest_employee` and `access_decision` aren't defined, so every request would crash with a 500 error. The nearest-employee search (pgvector `cosine_distance`, `similarity = 1 - distance`, threshold around 0.363) is what goes in their place. When it approves someone, it should also call `create_employee_log`.
4. **The API key isn't checked.** The Pi now sends `X-API-Key`, but only `/device/ping` checks it. Move that check into a small dependency and use it on the new route too:

   ```python
   def verify_device_key(x_api_key: str | None = Header(default=None)):
       if x_api_key is None or not secrets.compare_digest(x_api_key, os.environ["DEVICE_API_KEY"]):
           raise HTTPException(status_code=401, detail="Invalid API key")

   @recognition_router.post("/identify", response_model=RecognitionResponse,
                            dependencies=[Depends(verify_device_key)])
   ```

   `DEVICE_API_KEY` in the backend's `.env` must be identical to the one in the Pi's `.env`.
5. **Different embedding models.** The Pi computes **SFace** embeddings, but the backend saves **DeepFace Facenet** embeddings when employees are created. Until `get_embedding` in the backend uses the same YuNet and SFace models as the Pi, the similarities are meaningless. All four `.onnx` files are already in `raspberry-packages/model_weights`, so the backend can load the same two files. After that switch, existing employees need to be recreated.

## Running both on the same PC

- The Pi's `.env` has `DEVICE_ID=simulated-pi-01` and `BACKEND_URL=http://127.0.0.1:8000`, so the Pi is being simulated on the PC for now. That works with `127.0.0.1`.
- **Watch the ports.** The Pi package is also a FastAPI app (`main.py`, with `/camera/status` and `/camera/stream`). If you start both with plain `uvicorn`, both try to use port 8000. Run the Pi side on another port:

  ```powershell
  # backend, from the repo root
  uvicorn demo.app.app:app --reload --port 8000
  # simulated Pi, from raspberry-packages
  uvicorn main:app --port 8001
  ```

- On the real Pi later, change `BACKEND_URL` to the PC's network IP and start the backend with `--host 0.0.0.0`.

## The old `face_client.py`

It still checks `result.get("recognized")` and formats `similarity`, so it doesn't match the new `approved` contract. If `main.py` and `RecognitionService` replace it, it can be deleted. To keep it, change it to read `approved`.

## Summary of backend work

1. Add `POST /recognition/identify`, returning status 200 and the Pi's `RecognitionRequest`/`RecognitionResponse` schemas.
2. Add the API-key dependency.
3. Implement the nearest-employee search and threshold, and log approved entries.
4. Switch the backend's `get_embedding` to SFace, then recreate the employees.

Open decision: should denied attempts also be logged? That requires making `employee_uuid` nullable in the log table.
