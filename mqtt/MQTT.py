import asyncio
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
from utils import search_faces 
from chromadb_init import init_chromadb_wrapper
from chromadb.config import Settings
from aiomqtt import Client, MqttError

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "fastapi/topic"

async def mqtt_subscriber():
    """
    Background task that subscribes to an MQTT topic and logs incoming messages.
    """
    try:
        async with Client(MQTT_BROKER, port=MQTT_PORT) as client:
            # Subscribe to the topic.
            await client.subscribe(MQTT_TOPIC)
            print(f"Subscribed to {MQTT_TOPIC}")

            # Process messages as they arrive.
            async for message in client.messages:
                payload = message.payload.decode()
                print(f"Received message on topic '{message.topic}': {payload}")
    except MqttError as error:
        print(f"MQTT error: {error}")
