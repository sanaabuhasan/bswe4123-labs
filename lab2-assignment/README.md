Lab Assignment 2: Campus Room Booking Service

1. Project Description

This project implements a REST API for managing university rooms and bookings using FastAPI, Pydantic, and HTTPX.

The service allows users to create rooms, view rooms, create bookings, view bookings, and delete bookings.

It prevents overlapping bookings for the same room on the same day.

2. API Design

Operation| Method| URI| Request Body| Success Code| Error Codes
Get all rooms| GET| /rooms| None| 200| None
Create a room| POST| /rooms| id, building, capacity| 201| 409, 422
Get a room| GET| /rooms/{room_id}| None| 200| 404
Create a booking| PUT| /bookings/{booking_id}| room_id, day, start_hour, end_hour, purpose| 201 (new), 200 (retry)| 404, 409, 422
Get a booking| GET| /bookings/{booking_id}| None| 200| 404
Delete a booking| DELETE| /bookings/{booking_id}| None| 204| 404

Example Room Request

{
  "id": "B205",
  "building": "Engineering",
  "capacity": 30
}

Example Booking Request

{
  "room_id": "B205",
  "day": "2026-12-01",
  "start_hour": 10,
  "end_hour": 12,
  "purpose": "Study group"
}

3. Validation and Error Handling

- 200 OK: The request was successful, including an identical booking retry.
- 201 Created: A new room or booking was created.
- 204 No Content: A booking was deleted successfully.
- 404 Not Found: The requested room or booking does not exist.
- 409 Conflict: A room already exists, a booking overlaps another booking, or a booking ID is used with different data.
- 422 Unprocessable Entity: The submitted data is invalid, such as an end hour before the start hour or a capacity that is not positive.

4. Booking Overlap Prevention

The service checks whether an existing booking belongs to the same room and the same day.

Two bookings overlap when:

new_start < existing_end
AND
new_end > existing_start

This allows consecutive bookings. For example, a booking from 10:00 to 12:00 and another from 12:00 to 13:00 are allowed.

5. Safe Retry Design (Idempotency)

The service uses the PUT method with a booking ID selected by the client.

For example:

"PUT /bookings/BK001"

When the same request is sent again using the same booking ID and the same data, the existing booking is returned with status code 200 instead of creating another booking.

If the same booking ID is used with different data, the service returns 409 Conflict.

This design prevents duplicate bookings when a client retries a request because the original response was lost.

6. Testing

The "test_bookings.py" client uses HTTPX to test the API.

The following test cases were executed successfully:

Test Case| Expected Status| Actual Status
Create room| 201| 201
Duplicate room| 409| 409
Get all rooms| 200| 200
Get existing room| 200| 200
Get unknown room| 404| 404
Create booking| 201| 201
Retry same booking| 200| 200
Same ID with different data| 409| 409
Overlapping booking| 409| 409
Adjacent booking| 201| 201
Invalid booking hours| 422| 422
Booking unknown room| 404| 404
Get existing booking| 200| 200
Get unknown booking| 404| 404
Delete booking| 204| 204
Delete unknown booking| 404| 404
Delete adjacent booking| 204| 204

All 17 test cases passed with the expected HTTP status codes.

7. Technologies Used

- Python
- FastAPI
- Pydantic
- HTTPX
- Uvicorn

8. Project Structure

lab2-assignment/
│
├── service.py
├── test_bookings.py
└── README.md

9. Notes

The project currently uses in-memory storage. Therefore, rooms and bookings are reset when the server restarts.