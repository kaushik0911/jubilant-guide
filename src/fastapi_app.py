import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

REDPANDA_BROKER = "localhost:9092"
TOPIC_NAME = "roadblocks"

producer: Optional[AIOKafkaProducer] = None


class BlockStatus(str, Enum):
    BLOCKED = "blocked"
    PARTIALLY_BLOCKED = "partially-blocked"
    OPEN = "open"


class RoadblockCreate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    long: float = Field(..., ge=-180, le=180)
    status: BlockStatus


class RoadblockResponse(BaseModel):
    id: UUID
    lat: float
    long: float
    status: BlockStatus
    created_at: str


@app.on_event("startup")
async def startup_event():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=REDPANDA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()


@app.on_event("shutdown")
async def shutdown_event():
    global producer
    if producer:
        await producer.stop()


@app.post(
    "/blocker/create",
    response_model=RoadblockResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def add_blocker(payload: RoadblockCreate):
    event_id = uuid4()
    event_data = {
        "id": str(event_id),
        "lat": payload.lat,
        "long": payload.long,
        "status": payload.status.value,
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        await producer.send_and_wait(TOPIC_NAME, value=event_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to queue event: {str(e)}",
        )

    return event_data
