# Recognition flow and employee logs

How `Employee` and `EmployeeLog` are related in SQLAlchemy, and how to create and read logs when an employee is identified.

## How the relationship works

There are two layers, and the models in `models/` define both:

1. **In the database:** `EmployeeLog.employee_uuid` is a foreign key pointing at `employee.uuid`. This column is what actually links a log row to its employee. Postgres only knows about this part.
2. **In Python:** the `relationship()` attributes are a convenience layer SQLAlchemy builds on top of that foreign key:
   - `employee.employee_logs` is a list of that employee's `EmployeeLog` objects.
   - `log.employee` is the `Employee` object the log belongs to.

   `back_populates` keeps the two sides in sync. If you append a log to `employee.employee_logs`, its `log.employee` is set automatically, and the other way around.

So you never write SQL joins yourself. You either set the foreign key, or work through the relationship attributes and let SQLAlchemy fill in the foreign key for you.

## Creating a log

There are two equivalent ways to do it.

**Option A: set the foreign key directly.** This is simplest when all you have is the employee's id:

```python
log = EmployeeLog(employee_uuid=employee_id)
session.add(log)
session.commit()
```

**Option B: go through the relationship.** Use this when you already have the `Employee` object:

```python
employee.employee_logs.append(EmployeeLog())
session.commit()
```

SQLAlchemy fills in `employee_uuid` for you. You don't need `session.add()` because the employee is already in the session and the new log is attached to it.

In the recognition flow, recognition will already have found the matching `Employee`, so Option B fits naturally. Either way you don't set `uuid` or `timestamp`, because the model's defaults (`uuid4` and `datetime.now(timezone.utc)`) fill those in.

The function needs the session as a parameter:

```python
from models.employee_log import EmployeeLog

def create_employee_log(employee : Employee, session : Session) -> EmployeeLog:
    log = EmployeeLog()
    employee.employee_logs.append(log)
    session.commit()
    session.refresh(log)   # loads the generated uuid/timestamp from the DB
    return log
```

Returning the ORM object works because `employee_log_response` has `from_attributes=True`, so FastAPI can turn it into the response.

## Where it fits in the recognition flow

```
picture → get_embedding() → find the closest Employee by embedding → create_employee_log(employee, session)
```

For the "find closest" step, pgvector lets you sort by vector distance directly in the query:

```python
from sqlalchemy import select

def identify_employee(picture : Base64Bytes, session : Session) -> Employee | None:
    embedding = get_embedding(picture)
    stmt = (
        select(Employee)
        .order_by(Employee.embedding.cosine_distance(embedding))
        .limit(1)
    )
    return session.scalars(stmt).first()
```

In practice you'd also check the distance against a threshold. Otherwise an unknown person gets matched to whoever is closest.

## Reading logs back

Reading `employee.employee_logs` triggers a query for that employee's logs the first time you access it. `get_employees` returns every employee with their logs, so that would mean one extra query per employee. To load all the logs in a single extra query, use `selectinload`:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def get_employees(session : Session) -> list[Employee]:
    stmt = select(Employee).options(selectinload(Employee.employee_logs))
    return list(session.scalars(stmt))
```

Deleting already works across the relationship. The `cascade="all, delete-orphan"` and `ondelete="CASCADE"` settings mean that deleting an employee also deletes their logs.
