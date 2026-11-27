import asyncio
import os
from typing import Dict

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Campus Room Booking Service")


# Delay setting from environment variable
@app.middleware("http")
async def add_delay(request, call_next):
    delay = float(os.getenv("ROOM_SERVICE_DELAY", "0"))

    if delay > 0:
        await asyncio.sleep(delay)

    response = await call_next(request)
    return response


# Pydantic Models

class Room(BaseModel):
    id: str
    building: str
    capacity: int = Field(gt=0)


class Booking(BaseModel):
    room_id: str
    day: str
    start_hour: int = Field(ge=8, le=20)
    end_hour: int = Field(ge=8, le=20)
    purpose: str

    @model_validator(mode="after")
    def check_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("End hour must be after start hour")
        return self


# In-memory storage

rooms: Dict[str, Room] = {}
bookings: Dict[str, Booking] = {}


# Room Endpoints

@app.get("/rooms")
def get_rooms():
    return list(rooms.values())


@app.post("/rooms", status_code=status.HTTP_201_CREATED)
def create_room(room: Room):
    if room.id in rooms:
        raise HTTPException(
            status_code=409,
            detail="Room already exists"
        )

    rooms[room.id] = room
    return room


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in rooms:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    return rooms[room_id]


# Booking Endpoints

@app.put("/bookings/{booking_id}")
def create_booking(booking_id: str, booking: Booking):

    if booking.room_id not in rooms:
        raise HTTPException(
            status_code=404,
            detail="Room not found"
        )

    # Safe retry using the same booking ID
    if booking_id in bookings:
        if bookings[booking_id] == booking:
            return bookings[booking_id]

        raise HTTPException(
            status_code=409,
            detail="Booking ID already exists"
        )

    # Check overlapping bookings
    for existing in bookings.values():
        if (
            existing.room_id == booking.room_id
            and existing.day == booking.day
            and booking.start_hour < existing.end_hour
            and booking.end_hour > existing.start_hour
        ):
            raise HTTPException(
                status_code=409,
                detail="Booking time overlaps"
            )

    bookings[booking_id] = booking

    return JSONResponse(
        status_code=201,
        content=booking.model_dump()
    )


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return bookings[booking_id]


@app.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_booking(booking_id: str):
    if booking_id not in bookings:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    del bookings[booking_id]