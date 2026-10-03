from pydantic import BaseModel, Base64Bytes, ConfigDict
from datetime import datetime

from uuid import UUID

#HTTP request & response models

class employee_create_request(BaseModel):
    picture : Base64Bytes

class employee_log_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    timestamp : datetime

class employee_response(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid : UUID
    embedding : list[float]
    employee_logs : list[employee_log_response]
    
