# Notes

## Request and response models (`packages/Application/app.py`)

The `/employees` endpoints use two Pydantic models, one for each direction:

- **`EmployeeCreate`** (the function argument) controls **what comes in**. FastAPI validates the JSON
  request body against it. If a required field is missing or has the wrong type, FastAPI returns a
  `422` error and the function never runs.
- **`EmployeeOut`** (`response_model=` on the route) controls **what goes out**. Whatever the
  function returns is filtered through this model before it is turned into JSON.
  `from_attributes=True` lets it read a SQLAlchemy object (`new_emp.name`) instead of a dict.

Flow of one `POST /employees`:

```
client JSON ──► EmployeeCreate ──► create_employee() ──► return new_emp ──► EmployeeOut ──► response JSON
               (validates input)   (builds Employee,     (SQLAlchemy       (filters output)
                                    saves to DB)          object, all columns)
```

`new_emp` is not the HTTP response. It is only the function's return value, and FastAPI builds
the response from it using `EmployeeOut`.

Who provides each column:

| Column      | Provided by                  | Notes                                           |
|-------------|------------------------------|-------------------------------------------------|
| `id`        | database                     | auto-increment primary key                      |
| `name`      | client                       |                                                 |
| `picture`   | client                       | sent as base64 text (`Base64Bytes`), stored as bytes |
| `embedding` | client (for now)             | exactly 512 floats; may later be computed server-side from the picture |
| `approved`  | client, defaults to `false`  |                                                 |
| `logs`      | client, defaults to `[]`     |                                                 |
| `timestamp` | server (`datetime.now()`)    | the client should not choose it                 |

`picture` and `embedding` are **saved in the database but not included in the response**,
because `EmployeeOut` does not list them. They are left out for two reasons: they are large, and
raw bytes and numpy arrays can't be turned into JSON, so FastAPI would crash.






///////////////////////////////////////
**TODO:** `GET /employees` has no `response_model` yet, so it tries to return `picture` and
`embedding` and will fail. Fix: `@app.get("/employees", response_model=list[EmployeeOut])`.
//////////////////////////////////////






## Testing with base64 images

In the docs `picture` shows up as a **string**. That is expected, because JSON has no binary type.
The client sends the image as base64 text and FastAPI decodes it back into bytes.

Use a small image (a few hundred KB at most). Base64 makes a file about 33% larger, and very large
strings can freeze the Swagger page.

### Option 1: Swagger UI (`http://localhost:8000/docs`)

1. Copy the image as base64 (PowerShell):
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\photo.jpg")) | Set-Clipboard
   ```
2. Copy a dummy 512-number embedding:
   ```powershell
   python -c "import json; print(json.dumps([0.0]*512))" | Set-Clipboard
   ```
3. Open `POST /employees`, click **Try it out**, and paste both values into the body (one at a time):
   ```json
   {
     "name": "Vincent",
     "picture": "<base64 here>",
     "embedding": [<512 zeros here>],
     "approved": false,
     "logs": []
   }
   ```

### Option 2: Python script

Run this while the server is running:

```python
import base64
import requests

with open(r"C:\path\to\photo.jpg", "rb") as f:
    picture_b64 = base64.b64encode(f.read()).decode()

resp = requests.post("http://localhost:8000/employees", json={
    "name": "Vincent",
    "picture": picture_b64,
    "embedding": [0.0] * 512,
    "approved": False,
    "logs": [],
})
print(resp.status_code, resp.json())
```

### Checking that the picture was saved

The response does not include the picture, so check the database directly (psql or pgAdmin):

```sql
SELECT id, name, length(picture) AS picture_bytes FROM employee;
```

`picture_bytes` should match the file's size on disk.

If the POST fails with a missing-column error, the `employee` table from before the model change
still exists. `Base.metadata.create_all` only creates missing tables and never adds columns. In
development, run `DROP TABLE employee;` and restart the server so the table is recreated.
