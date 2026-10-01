from pydantic import BaseModel, Base64Bytes
from datetime import datetime

import uuid

#HTTP request & response models

class employee_create_request(BaseModel):
    picture : Base64Bytes

class employee_log_response(BaseModel):
    timestamp : datetime

class employee_response(BaseModel):
    uuid : uuid
    embedding : list[float]
    employee_logs : list[employee_log_response]
    
