import os
import uuid
from dotenv import load_dotenv
from supabase import create_client, Client
from infra.schema.models import AccessLog, SecurityWarning
from infra.schema.enums import AccessAction
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)
print("Supabase client created successfully.")

# Generate a valid UUID for user_id
user_id = str(uuid.uuid4())

# Insert the user into the "users" table if it doesn't already exist
user_response = supabase.table("users").insert([
    {
        "id": user_id,  # Use the generated UUID
        "name": "Test User",  # Add other required fields for the "users" table
        "status": "active",  # Provide a valid value for the "status" column
        "created_at": datetime.utcnow().isoformat(),
    }
]).execute()
print("User inserted successfully:", user_response)

# Create an instance of AccessLog
access_log = AccessLog(
    room_number="101",
    userId=user_id,  # Use the generated UUID
    action=AccessAction.ENTER  # Use a valid enum value like AccessAction.ENTER or AccessAction.EXIT
)

# Insert AccessLog into Supabase
access_log_response = supabase.table("access_logs").insert([
    {
        "room_number": access_log.room_number,
        "user_id": access_log.userId,
        "action": access_log.action.value,  # Use the enum value
        "timestamp": datetime.utcnow().isoformat(),
    }
]).execute()
print("AccessLog inserted successfully:", access_log_response)

# Create an instance of SecurityWarning
try:
    security_warning = SecurityWarning(
        type='unauthorized-access',
        room_number="101",
        status='critical',  # Use a valid enum value
        description="Unauthorized access detected",
        userId=user_id  # Use the same generated UUID
    )
except Exception as e:
    print("Error creating SecurityWarning instance:", str(e))
else:
    print("SecurityWarning instance created successfully.")

try:
    # Insert SecurityWarning into Supabase
    security_warning_response = supabase.table("security_warnings").insert([
        {
            "type": security_warning.type,
            "room_number": security_warning.room_number,
            "status": security_warning.status.value,  # Use the enum value
            "description": security_warning.description,
            "user_id": security_warning.userId,
            "created_at": datetime.utcnow().isoformat(),
        }
    ]).execute()
except Exception as e:
    print("Error inserting SecurityWarning:", str(e))
else:
    # If the insert was successful, print the response
    print("SecurityWarning inserted successfully:", security_warning_response)
try:
    security_warning_response = supabase.table("security_warnings").insert([
        {
            "type": security_warning.type,
            "room_number": security_warning.room_number,
            "status": security_warning.status,
            "description": security_warning.description,
            "user_id": security_warning.userId,
            "created_at": datetime.utcnow().isoformat(),
        }
    ]).execute()
except Exception as e:
    print("Error inserting SecurityWarning:", str(e))
else:
    print("SecurityWarning inserted successfully:", security_warning_response)