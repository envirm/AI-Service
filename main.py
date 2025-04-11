# main.py

import asyncio
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
from utils import search_faces 
from chromadb_init import init_chromadb_wrapper
from chromadb.config import Settings
from infra.mqtt.MQTT import mqtt_subscriber
from aiomqtt import Client, MqttError
from infra.schema.supasbase import supabase, AccessLog, SecurityWarning
from datetime import datetime
from infra.schema.enums import AccessAction
from infra.redis.pub import *  # Import the AccessAction enum
from fastapi.middleware.cors import CORSMiddleware
from handler.securityhand import securityWarning_handler, resolve_security_warning

MQTT_BROKER = "test.mosquitto.org"  # Replace with your MQTT broker address
MQTT_PORT = 1883
MQTT_TOPIC = "fastapi/topic"

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0",
    description="A simple FastAPI project starter guide"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
    """
    On startup, start the MQTT subscriber task.
    """
    global collection  # Declare collection as a global variable
    asyncio.create_task(mqtt_subscriber())
    global redisClient  # Declare redisClient as a global variable
    redisClient = init_redis_connection()
    print("MQTT subscriber task started.")

    _, collection = init_chromadb_wrapper()

@app.get("/")
def read_root():
    """
    Root endpoint returning a welcome message.
    """
    return {"message": "Welcome to my FastAPI project!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """
    Endpoint to retrieve an item by its ID.
    Optional query parameter 'q' can be provided.
    """
    return {"item_id": item_id, "q": q}

@app.post("/publish/{msg}")
async def publish_message(msg: str, background_tasks: BackgroundTasks):
    """
    Endpoint to publish a message to the MQTT topic.
    This function launches a background task to publish the message.
    """
    async def publish():
        try:
            async with Client(MQTT_BROKER, port=MQTT_PORT) as client:
                await client.publish(MQTT_TOPIC, msg)
                print(f"Published message: {msg} to topic: {MQTT_TOPIC}")
        except MqttError as error:
            print(f"Failed to publish message: {error}")

    background_tasks.add_task(publish)
    return {"status": "Publish initiated", "message": msg}
@app.post("/recognize-face/{lock_id}")
async def recognize_face(lock_id: str, file: UploadFile = File(...)):
    global collection  # Access the global collection variable
    global redisClient  # Access the global redisClient variable
async def recognize_face(lock_id: str, file: UploadFile = File(...)):
    """
    Endpoint to perform face recognition on an uploaded image.
    """
    try:
        reauired= lock_id.split("/")[0]
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        name,grade = search_faces(temp_file_path, collection)
        if grade != reauired:
            await publish_message(f"noaccess")
            publish_message_R(redisClient, lock_id, f"noaccess")
            os.remove(temp_file_path)
            return JSONResponse(content={"status": "error", "message": "Face not recognized!"}, status_code=300)
        
        await publish_message(f"access")

        # Clean up the temporary file
        os.remove(temp_file_path)
        publish_message_R(redisClient, lock_id, f"access")    

        return JSONResponse(content={"status": "success", "message": "Face recognized successfully!"})

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

   

@app.post("/insert-access-log/")
async def insert_access_log(room_number: str, user_id: str, action: AccessAction):

    try:
        # Create an AccessLog instance with the provided enum value
        access_log = AccessLog(
            room_number=room_number,
            userId=user_id,
            action=action  # Use the enum directly
        )
        response = supabase.table("access_logs").insert([
            {
                "room_number": access_log.room_number,
                "user_id": access_log.userId,
                "action": access_log.action.value,  # Use the enum value
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]).execute()
        return JSONResponse(content={"status": "success", "message": "AccessLog inserted successfully!", "response": response.data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/insert-security-warning/")
async def insert_security_warning(room_number: str, user_id: str, warning_type: str, status: str, description: str):
    """
    Endpoint to insert a SecurityWarning into Supabase.
    """
    try:
        security_warning = SecurityWarning(
            type=warning_type,
            room_number=room_number,
            status=status,
            description=description,
            userId=user_id
        )
        response = supabase.table("security_warnings").insert([
            {
                "type": security_warning.type,
                "room_number": security_warning.room_number,
                "status": security_warning.status,
                "description": security_warning.description,
                "user_id": security_warning.userId,
            }
        ]).execute()
        return JSONResponse(content={"status": "success", "message": "SecurityWarning inserted successfully!", "response": response.data})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

@app.post("/security-warning/")
async def create_security_warning(user_id: str, room_number: str):
    """
    Route to handle security warning creation.
    """
    try:
        await securityWarning_handler(user_id, room_number)
        return {"status": "success", "message": "Security warning created successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/security-warning/{warning_id}/resolve/")
async def resolve_security_warning_route(warning_id: str):
    """
    Route to resolve a security warning.
    """
    try:
        response = await resolve_security_warning(warning_id)
        return {"status": "success", "message": "Security warning resolved successfully.", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/security-warnings/")
async def get_all_security_warnings():
    """
    Route to fetch all security warnings from Supabase.
    """
    try:
        # Fetch all security warnings from the database
        response = supabase.table("security_warnings").select("*").execute()
        if response.data:
            return JSONResponse(content={"status": "success", "data": response.data})
        else:
            return JSONResponse(content={"status": "success", "message": "No security warnings found."})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)

# grade we git it from mobile route grade/lock_id
