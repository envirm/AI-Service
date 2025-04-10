# main.py

import asyncio
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
from utils import search_faces 
from chromadb_init import init_chromadb_wrapper
from chromadb.config import Settings
from mqtt.MQTT import mqtt_subscriber
from aiomqtt import Client, MqttError

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "fastapi/topic"
 # Assuming you have a module named utils with a function search_faces   
# from face_recognition_module import search_faces
# Ensure the module is installed or replace it with the correct module name

# Import the search_faces function
app = FastAPI(
    title="My FastAPI Project",
    version="1.0.0",
    description="A simple FastAPI project starter guide"
)
# Configure MQTT broker details.
@app.on_event("startup")
async def startup_event():
    """
    On startup, start the MQTT subscriber task.
    """
    asyncio.create_task(mqtt_subscriber())
    print("MQTT subscriber task started.")


_ , collection = init_chromadb_wrapper()
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
            # Connect to the MQTT broker and publish the message.
            async with Client(MQTT_BROKER, port=MQTT_PORT) as client:
                await client.publish(MQTT_TOPIC, msg)
                print(f"Published message: {msg} to topic: {MQTT_TOPIC}")
        except MqttError as error:
            print(f"Failed to publish message: {error}")

    # Launch the publishing task in the background.
    background_tasks.add_task(publish)
    return {"status": "Publish initiated", "message": msg}

@app.post("/recognize-face/")
async def recognize_face(file: UploadFile = File(...)):
    """
    Endpoint to perform face recognition on an uploaded image.
    """
    try:
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        search_faces(temp_file_path,collection)  # Call your face recognition function here
        #send signal through MQTT
        # HTTPX send log for the user get in 
        # Call your face recognition function here
        # Replace the following line with your actual face recognition logic
        result = {"status": "success", "message": "Face recognized successfully!"}

        # Clean up the temporary file
        os.remove(temp_file_path)

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
    # send signal through MQTT in case the user is unauthorized and got in
