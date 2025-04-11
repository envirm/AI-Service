from datetime import time
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_generator():
    while True:
        await asyncio.sleep(1)  
        yield f"data: Security warning at {time.time()}\n\n"

@app.get("/security-warning")
async def security_warning():
    return StreamingResponse(event_generator(), media_type="text/event-stream")