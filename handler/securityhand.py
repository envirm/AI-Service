import asyncio
from infra.schema import enums
from infra.redis.pub import publish_message_R
from datetime import datetime
from infra.schema import supasbase 

async def securityWarning_handler(user_id: str, room_number: str):
    """
    Handler for security warning events.
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
        print(f"Error in securityWarning_handler: {e}")

async def resolve_security_warning(warning_id: str):
    """
    Handler for resolving a security warning.
    """
    try:
        # Update the SecurityWarning status to RESOLVED in the database
        response = supasbase.update_security_warning_status(warning_id, enums.WarningStatus.RESOLVED.value)
        
        # Publish a message to the Redis channel
        await publish_message_R("id", {"warning_id": warning_id, "status": "RESOLVED"})
        print(f"Security warning with ID {warning_id} resolved successfully.")
        return response
    except Exception as e:
        print(f"Error in resolve_security_warning: {e}")
        return {"status": "error", "message": str(e)}
