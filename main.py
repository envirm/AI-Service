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
from infra.schema.enums import AccessAction  # Import the AccessAction enum

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "fastapi/topic"

app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0",
    description="A simple FastAPI project starter guide"
)

@app.on_event("startup")
async def startup_event():
    """
    On startup, start the MQTT subscriber task.
    """
    asyncio.create_task(mqtt_subscriber())
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

@app.post("/publish/{msg}",response_model=200)
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
    """
    Endpoint to perform face recognition on an uploaded image.
    """
    try:
        reauired= lock_id.split("/")[0]
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)

        client= mqtt_subscriber()
        name,grade = search_faces(temp_file_path, collection)
        if grade != reauired:
            await mqtt_subscriber.publish(f"noaccess")
        await mqtt_subscriber.publish(f"access")

        # Clean up the temporary file
        os.remove(temp_file_path)
       

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
# grade we git it from mobile route grade/lock_id 