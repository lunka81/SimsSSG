# Registering an employee as admin

> **Question:** When a new employee is registered and the role "admin" is picked, a pop-up should appear asking for a username and a password (since admins need those). Aside from the frontend aspects, what is the next step here?

The backend needs to handle one form submission that sometimes contains an admin account, and it must handle it **all-or-nothing**. Here are the steps in order.

## 1. Decide what "admin" means: role, or account?

The `Permission` enum already has an `Admin` value, and there's also the `admin` table. The pop-up ties them together: choosing **Admin** in the dropdown means "this person gets a login". Make that a firm rule:

- `permission == Admin` → the employee **must** have an admin account.
- Any other permission → the employee **must not** have one.

Otherwise the two can drift apart. There could be an "Admin" employee who can't log in, or a "Limited" employee who can log in to the admin page.

## 2. One request, with the login details as an optional part

The pop-up is only a frontend step. When the admin clicks "Add person", the frontend should still send **one** request containing everything:

```json
{
  "name": "Anna Svensson",
  "permission": "Admin",
  "description": "IT",
  "img": "data:image/jpeg;base64,...",
  "admin_account": { "username": "anna", "password": "..." }
}
```

For other roles, `admin_account` is left out or set to `null`. In the schema, that looks like this:

```python
class AdminAccountCreate(BaseModel):
    username: str
    password: str = Field(min_length=8)

class EmployeeCreate(BaseModel):
    name: str
    permission: Permission
    description: str | None = None
    img: str
    admin_account: AdminAccountCreate | None = None

    # enforces the rule from step 1 before any code runs
    @model_validator(mode="after")
    def admin_needs_account(self):
        if (self.permission == Permission.ADMIN) != (self.admin_account is not None):
            raise ValueError("Admins need a username and password, and only admins can have them")
        return self
```

The validator runs before the route does. A request that breaks the rule gets a **422** automatically, so the rest of the code can trust the data. With this, `AdminCreate` is no longer needed, and `POST /api/employee/` handles both cases.

## 3. Save both in one transaction

`add_employee` currently calls `commit()` itself. Creating an admin afterwards is then a *second* save. If that second save fails, for example because the username is taken, the employee has already been stored, but without the account that its "Admin" role requires.

The fix is to commit **once**, at the end:

```python
def add_employee(session: Session, data: EmployeeCreate) -> EmployeeTest:
    img_bytes, bgr = decode_image_to_bgr(data.img)
    employee = EmployeeTest(
        name=data.name, permission=data.permission, description=data.description,
        image=img_bytes, embedding=get_embedding(bgr),
    )
    if data.admin_account is not None:
        employee.admin = Admin(
            username=data.admin_account.username,
            password_hash=password_hasher.hash(data.admin_account.password),
        )
    session.add(employee)
    try:
        session.commit()          # employee and admin are saved together, or not at all
    except IntegrityError:
        session.rollback()
        raise UsernameTaken()     # the route turns this into a 409
    session.refresh(employee)
    return employee
```

- **`employee.admin = Admin(...)`** links the two through the existing relationship. SQLAlchemy fills in `employee_uuid` itself and saves both rows.
- **`IntegrityError`** is what the database raises when `unique=True` on `username` is broken. Catching it also covers the rare case where two requests use the same username at the same moment, which the `username_unique` pre-check can't prevent.

## 4. Keep the rule true after registration too

- **Changing someone's permission** (the future edit endpoint): changing *to* Admin must also create an account, so it needs a username and password too. Changing *away from* Admin must delete the account. Set `employee.admin = None`, and the `delete-orphan` cascade removes the row.
- **Deleting an employee** already removes their admin account, thanks to the cascade.
- **Protect the endpoint with `get_current_admin`.** Otherwise anyone can create an admin account for themselves. A one-off script is still needed for creating the very first admin.

## 5. What happens to `/auth/register`

Once `POST /api/employee/` can create admins, `/auth/register` and `AdminCreate` do the same job twice. Remove them, and keep `/auth/login` as the only route in `login_router`.

## Order to do it in

1. Schema and validator (steps 1–2).
2. `add_employee` with a single commit (step 3).
3. Protect the route and remove `/auth/register` (steps 4–5).

Rules for editing permissions can wait until the edit endpoint is built.
