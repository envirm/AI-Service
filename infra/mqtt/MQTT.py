import asyncio
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
import shutil
import os
from infra.redis.pub import publish_message_R
from infra.schema.enums import WarningStatus,WarningType
from infra.schema.enums import AccessAction
from handler.accesslog import access_granted_handler, access_denied_handler
from handler.securityhand import securityWarning_handler

from utils import search_faces 
from chromadb_init import init_chromadb_wrapper
from chromadb.config import Settings
from aiomqtt import Client, MqttError

MQTT_BROKER = "192.168.137.114"
MQTT_PORT = 1883
MQTT_TOPIC = "fastapi/topic"
async def mqtt_subscriber() -> Client:
    """
    Background task that subscribes to an MQTT topic and logs incoming messages.
    Expects payloads in the format "command/lock_id/userid" and switches based on the command.
    """
    try:
        async with Client(MQTT_BROKER, port=MQTT_PORT, username="your_username", password="your_password") as client:
            # Subscribe to the topic.
            await client.subscribe(MQTT_TOPIC)
            print(f"Subscribed to {MQTT_TOPIC}")

            # Process messages as they arrive.
            async for message in client.messages:
                payload = message.payload.decode()
                print(f"Received message on topic '{message.topic}': {payload}")

                # Split the payload string by "/" to extract the command and additional information.
                parts = payload.split("/")
                # Make sure there's at least one part to process.
                if len(parts) > 0:
                    command = parts[0].strip()  # This will be the 'message' part in the format.
                    
                    if command == "warning":
                        print("Warning action triggered.")
                        securityWarning_handler(parts[1], parts[2])

                        # Call the redis publish_message_R function with additional parameters.
                        # Ensure redisClient is imported
                        # publish_message_R(redisClient, WarningType.value, payload)
                    elif command == "access_denied":
                        print("Access denied action triggered.")
                        access_denied_handler(parts[1], parts[2])
                        print("Access denied action triggered.")
                        # publish_message_R(redisClient, AccessAction.ACCESS_DENIED.value, payload)
                    elif command == "access_granted":
                        access_granted_handler(parts[1], parts[2])
                        print("Access granted action triggered.")
                        # publish_message_R(redisClient,AccessAction.ENTER)
                        print("Mandana command triggered.")
                    else:
                        print(f"Unrecognized command: {command}")
                else:
                    print("Received an invalid payload format.")

            return client
    except MqttError as error:
        print(f"MQTT error: {error}")
        return None

async def publish_message(msg: str,client: Client) -> None:
    """
    Publish a message to the MQTT topic.
    """
    try:
        await client.publish(MQTT_TOPIC, msg)
        print(f"Published message: {msg} to topic: {MQTT_TOPIC}")
    except MqttError as error:
        print(f"Failed to publish message: {error}")
