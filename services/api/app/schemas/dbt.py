from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DBTTransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class DBTTransactionResponse(BaseModel):
    application_id: UUID
    status: DBTTransactionStatus
    transaction_id: str
    amount: float
    created_at: datetime