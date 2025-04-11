from enum import Enum

class UserStatus(str, Enum):
    active = "active"
    in_room = "in-room"
    off_shift = "off-shift"

class AccessAction(str, Enum):
    ENTER = "enter"
    EXIT = "exit"

class ShiftAction(str, Enum):
    start = "start"
    end = "end"

class WarningType(str, Enum):
    unauthorized_access = "unauthorized-access"
    door_forced = "door-forced"
    extended_access = "extended-access"
    unusual_hours = "unusual-hours"

class WarningStatus(str, Enum):
    critical = "critical"
    warning = "warning"
    resolved = "resolved"
