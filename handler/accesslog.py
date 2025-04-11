import asyncio
from infra.schema import enums
from infra.redis.pub import publish_message_R
from datetime import datetime
from infra.schema import supasbase

async def access_granted_handler(user_id: str, room_number: str):
    """
    Handler for access granted events.
    """
    try:
        # Create an AccessLog entry
        access_log = supasbase.AccessLog(
            userId=user_id,
            room_number=room_number,
            action=enums.AccessAction.ENTER.value,
            timestamp=datetime.utcnow()
        )
        
        # Insert the AccessLog entry into the database
        await supasbase.insert_access_log(access_log)
        
        # Publish a message to the Redis channel
        await publish_message_R("access_granted", access_log.json())
        print(f"Access granted for user {access_log.userId} in room {access_log.room_number}")
    except Exception as e:
        print(f"Error in access_granted_handler: {e}")

async def access_denied_handler(user_id: str, room_number: str):
    """
    Handler for access denied events.
    """
    try:
        # Create an AccessLog entry
        access_log = supasbase.AccessLog(
            userId=user_id,
            room_number=room_number,
            action=enums.AccessAction.EXIT.value,
            timestamp=datetime.utcnow()
        )
        
        # Insert the AccessLog entry into the database
        await supasbase.insert_access_log(access_log)
        
        # Publish a message to the Redis channel
        await publish_message_R("access_denied", access_log.json())
        print(f"Access denied for user {access_log.userId} in room {access_log.room_number}")
    except Exception as e:
        print(f"Error in access_denied_handler: {e}")

async def warning_handler(user_id: str, room_number: str):
    """
    Handler for warning events.
    """
    try:
        # Create a SecurityWarning entry
        security_warning = supasbase.SecurityWarning(
            type=enums.WarningType.unauthorized_access.value,
            room_number=room_number,
            status=enums.WarningStatus.ACTIVE,
            description="Unauthorized access attempt detected.",
            userId=user_id,
            timestamp=datetime.utcnow()
        )
        
        # Insert the SecurityWarning entry into the database
        await supasbase.insert_security_warning(security_warning)
        
        # Publish a message to the Redis channel
        await publish_message_R("warning", security_warning.json())
        print(f"Security warning for user {security_warning.userId} in room {security_warning.room_number}")
    except Exception as e:
        print(f"Error in warning_handler: {e}")