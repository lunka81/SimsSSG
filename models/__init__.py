# Import every model so they're all registered on Base.metadata before
# relationships are resolved or tables are created.
from models.employee import Employee
from models.employee_log import EmployeeLog
