import os
import time
import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, model_validator

app = FastAPI(title="Exam Scheduler Service")

# Environment Variables
ROOM_SERVICE_URL = os.getenv(
    "ROOM_SERVICE_URL",
    "http://127.0.0.1:8002"
).rstrip("/")

ROOM_SERVICE_TIMEOUT = float(
    os.getenv("ROOM_SERVICE_TIMEOUT", "2")
)

ROOM_SERVICE_MAX_RETRIES = int(
    os.getenv("ROOM_SERVICE_MAX_RETRIES", "3")
)

# Store exam bookings to prevent duplicate exams
scheduled_exams = {}


class Exam(BaseModel):
    id: str
    course_code: str
    day: str
    start_hour: int = Field(ge=8, le=20)
    end_hour: int = Field(ge=8, le=20)
    students: int = Field(gt=0)

    @model_validator(mode="after")
    def check_hours(self):
        if self.end_hour <= self.start_hour:
            raise ValueError("End hour must be after start hour")
        return self


def send_request(method, url, **kwargs):
    for attempt in range(ROOM_SERVICE_MAX_RETRIES + 1):
        try:
            with httpx.Client(
                timeout=ROOM_SERVICE_TIMEOUT
            ) as client:
                response = client.request(
                    method, url, **kwargs
                )

            if response.status_code >= 500:
                if attempt < ROOM_SERVICE_MAX_RETRIES:
                    delay = 0.5 * (2 ** attempt)
                    print(f"Retry after {delay} seconds")
                    time.sleep(delay)
                    continue

            return response

        except (httpx.TimeoutException, httpx.ConnectError):
            if attempt < ROOM_SERVICE_MAX_RETRIES:
                delay = 0.5 * (2 ** attempt)
                print(f"Retry after {delay} seconds")
                time.sleep(delay)
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Room Booking Service is unavailable"
                )

    raise HTTPException(
        status_code=503,
        detail="Room Booking Service is unavailable"
    )


@app.get("/config")
def get_config():
    return {
        "room_service_url": ROOM_SERVICE_URL,
        "timeout": ROOM_SERVICE_TIMEOUT,
        "max_retries": ROOM_SERVICE_MAX_RETRIES
    }


@app.post("/exams", status_code=201)
def create_exam(exam: Exam):

    # Prevent duplicate exam requests
    if exam.id in scheduled_exams:
        if scheduled_exams[exam.id]["exam"] == exam:
            return scheduled_exams[exam.id]["result"]

        raise HTTPException(
            status_code=409,
            detail="Exam ID already exists"
        )

    response = send_request(
        "GET",
        f"{ROOM_SERVICE_URL}/rooms"
    )

    if response.status_code >= 500:
        raise HTTPException(
            status_code=503,
            detail="Room Booking Service error"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=503,
            detail="Could not retrieve rooms"
        )

    rooms = response.json()

    suitable_rooms = [
        room for room in rooms
        if room["capacity"] >= exam.students
    ]

    suitable_rooms.sort(
        key=lambda room: room["capacity"]
    )

    for room in suitable_rooms:
        booking = {
            "room_id": room["id"],
            "day": exam.day,
            "start_hour": exam.start_hour,
            "end_hour": exam.end_hour,
            "purpose": f"Exam {exam.course_code}"
        }

        booking_id = f"EXAM-{exam.id}"

        booking_response = send_request(
            "PUT",
            f"{ROOM_SERVICE_URL}/bookings/{booking_id}",
            json=booking
        )

        if booking_response.status_code in (200, 201):
            result = {
                "exam_id": exam.id,
                "course_code": exam.course_code,
                "booked_room": room,
                "booking_id": booking_id,
                "status": "booked"
            }

            scheduled_exams[exam.id] = {
                "exam": exam,
                "result": result
            }

            return result

        if booking_response.status_code == 409:
            continue

        if booking_response.status_code >= 500:
            raise HTTPException(
                status_code=503,
                detail="Room Booking Service error"
            )

        if booking_response.status_code == 404:
            continue

        raise HTTPException(
            status_code=503,
            detail="Could not book room"
        )

    raise HTTPException(
        status_code=409,
        detail="No free room large enough for this exam"
    )