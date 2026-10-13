# The get_current_admin dependency, in simple terms

> **Question:** Explain the `get_current_admin` code in simpler terms.

## The code

```python
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from demo.db.database import get_session

# Reads "Authorization: Bearer <token>" and adds an "Authorize" button to /docs
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> Admin:
    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

    #1. no token at all
    if credentials is None:
        raise unauthorized

    #2-3. checks signature and expiry, reads who the token belongs to
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        admin_uuid = UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized

    #4. the admin may have been deleted after the token was created
    admin = session.get(Admin, admin_uuid)
    if admin is None:
        raise unauthorized

    #5. routes can use this to know who is logged in
    return admin
```

## The explanation

Think of `get_current_admin` as a **guard at the door** of every admin page. Before anyone gets in, the guard checks their "wristband", which is the token. If anything looks wrong, they're turned away with "401: not authenticated".

### Setting up the guard

```python
bearer_scheme = HTTPBearer(auto_error=False)
```

This is a ready-made helper from FastAPI that knows where to **find** the wristband: in a request header that looks like `Authorization: Bearer eyJhbGci...`. It takes the token out of that header. `auto_error=False` just means "if there's no token, tell me instead of handling it yourself", so the code decides what happens.

### The function's inputs

```python
def get_current_admin(
    credentials = Depends(bearer_scheme),
    session = Depends(get_session),
):
```

This function is never called directly. FastAPI calls it automatically and hands it two things:

- **`credentials`**: the token it found in the header, or `None` if there was none.
- **`session`**: a database connection, so the guard can look things up.

### The rejection message, prepared once

```python
unauthorized = HTTPException(status_code=401, detail="Not authenticated", ...)
```

This is the "you can't come in" answer. It's written once and reused for every kind of failure, so the visitor never learns *why* they were turned away.

### Check 1: is there a wristband at all?

```python
if credentials is None:
    raise unauthorized
```

No token means no entry.

### Check 2: is the wristband real and still valid?

```python
try:
    payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    admin_uuid = UUID(payload["sub"])
except (...):
    raise unauthorized
```

- `jwt.decode` checks two things in one go:
  - **Is it genuine?** It recomputes the signature with the secret key. A forged or edited token won't match.
  - **Has it expired?** It compares `exp` with the current time.

  If both are fine, it gives back the contents, e.g. `{"sub": "c2424663-...", "exp": ...}`.
- `payload["sub"]` reads *who* the wristband belongs to, and `UUID(...)` turns that text back into a proper id.
- `try` / `except` means "if anything at all goes wrong in these lines, turn them away". That covers a fake token, an expired token, a garbled string, or a missing `sub`.

### Check 3: does this person still exist?

```python
admin = session.get(Admin, admin_uuid)
if admin is None:
    raise unauthorized
```

The wristband can be genuine and still belong to an admin who has since been deleted. Looking them up in the database makes sure deleted admins lose access straight away.

### Let them in

```python
return admin
```

Every check passed. The guard steps aside, and the actual route runs. The guard also passes the admin along, in case the route wants to know who's logged in.

### Putting the guard on a door

```python
employee_router = APIRouter(prefix="/api/employee", dependencies=[Depends(get_current_admin)])
```

This puts the guard in front of **every** route in the employee router at once. Each request is checked before the route runs, so the check doesn't need to be added to each route by hand.

## In short

**Find the token → check that it's genuine and not expired → check whose it is → check that the person still exists → let them in.** If any step fails, the answer is 401.
