from typing import Optional, List
from pydantic import BaseModel
from infra.schema.enums import (
    UserStatus,
    AccessAction,
    ShiftAction,
    WarningType,
    WarningStatus
)

class SecurityWarning(BaseModel):
    """
    Model representing a security warning.
    """
    type: WarningType
    room_number: str

    status: WarningStatus
    description: str
    userId: str
class AccessLog(BaseModel):
    """
    Model representing an access log entry.
    """
    userId: str
    room_number: str
    action: AccessAction
