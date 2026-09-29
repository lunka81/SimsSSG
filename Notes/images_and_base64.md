# Images and base64

## Q: Why is transferring and storing images a problem? The image is stored as raw bytes in Postgres, but converted to base64 when sent in JSON, right?

Yes, that's right. The only difficulty is that **JSON can only carry text, and an image isn't text.**

### Why raw bytes don't fit in JSON

An image file is a long list of bytes, where each byte is a number from 0 to 255. Many of those
numbers don't correspond to any readable character. Some are invisible control codes. Some happen
to equal `"` or `}`, which would end the JSON string or the object early. And some combinations
aren't valid text at all. If you pasted the raw bytes into a JSON string, the JSON would be broken.

### What base64 does

Base64 rewrites the bytes using only 64 safe characters: `A–Z`, `a–z`, `0–9`, `+` and `/`.
Every 3 bytes become 4 of these characters.

```
raw bytes:   255 216 255 224 ...        (can't go in JSON)
base64:      "/9j/4AAQSkZJRg..."        (plain text, fits in a JSON string)
```

Nothing is lost, and decoding gives back exactly the same bytes. The cost is that the data gets
about 33% bigger.

### Where each format is used

```
Client              ──JSON──►         FastAPI          ──►     Postgres
reads photo.jpg      picture as         Base64Bytes             stores raw bytes
encodes to base64    base64 text        decodes to bytes        (bytea column)
```

- **Postgres stores raw bytes.** A `bytea` column is built for binary data, so no conversion is
  needed and it takes the least space.
- **Base64 is only for the trip inside JSON.** It's packaging for transport, not how the image is
  stored.

### On the way back out

The image is **not** sent back as base64 by default: `EmployeeOut` leaves it out completely. A
separate `/employees/{id}/picture` endpoint can skip JSON altogether. It sends the raw bytes with
the header `Content-Type: image/jpeg`, which is exactly how any image loads on the web, so a
browser `<img>` tag can show it directly, with no base64 and no size increase:

```python
from fastapi import Response

@app.get("/employees/{emp_id}/picture")
def get_picture(emp_id: int, db: Session = Depends(get_db)):
    emp = db.get(Employee, emp_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return Response(content=emp.picture, media_type="image/jpeg")
```

```tsx
<ImageCard title="Database Image" image={`http://localhost:8000/employees/${id}/picture`} />
```

**In short:** raw bytes wherever binary data is allowed (the database, and image responses), and
base64 only when the image has to travel inside JSON.

---

## Q: Is there no way to simply include the base64 version of the image in EmployeeOut and have React decode it?

Yes, you can do that. There's one catch on the Python side, and on the React side it's simpler
than you might expect.

### Backend: encode the bytes in the output model

`Base64Bytes` doesn't work in this direction. On the way in, it **decodes** whatever it receives,
so if you give it the raw bytes from the database it tries to decode those as base64 and fails.
Instead, declare the field as plain `bytes` and tell Pydantic how to turn it into JSON:

```python
import base64
from pydantic import field_serializer

class EmployeeWithPicture(EmployeeOut):      # everything in EmployeeOut, plus the picture
    picture: bytes

    @field_serializer("picture")
    def encode_picture(self, v: bytes) -> str:
        return base64.b64encode(v).decode()   # raw bytes -> base64 text for the JSON
```

The response then looks like `{"id": 1, "name": "Vincent", ..., "picture": "/9j/4AAQSkZJRg..."}`.

### Frontend: no decoding needed

React doesn't have to decode anything. Browsers understand a **data URL**, which is an image
address containing the base64 text itself:

```tsx
<img src={`data:image/jpeg;base64,${emp.picture}`} />
```

The browser decodes it when it displays the image. That also works with `ImageCard`, since its
`image` prop just takes a string:

```tsx
<ImageCard title="Database Image" image={`data:image/jpeg;base64,${emp.picture}`} />
```

### When to use this

It's a good fit when a response concerns **one** employee. For example, the Home page's
recognition result could return the name, confidence and picture together in a single request.

Avoid it for **lists**. If `GET /employees` included every picture, the response would grow by the
size of every image each time someone is added, and all of them would download on every page load
even when nobody looks at them. Separate picture URLs load only when an image is actually shown,
and the browser can cache them.

That's why this is a separate `EmployeeWithPicture` model instead of adding `picture` to
`EmployeeOut`. Use it as the `response_model` on single-employee endpoints, and keep the list
endpoint lightweight.
