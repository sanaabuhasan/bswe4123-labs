Lab Assignment 3: Exam Scheduler Service

1. Project Description

This project implements an Exam Scheduler Service using FastAPI. It communicates with a Room Booking Service to find and reserve suitable rooms for university exams.

2. Project Files

- "scheduler.py": Exam Scheduler Service.
- "room_service.py": Room Booking Service.
- "README.md": Project documentation and test results.

3. How to Run the Services

Room Booking Service

Open PowerShell in the "lab3-assignment" folder and run:

$env:ROOM_SERVICE_DELAY="0"
python -m uvicorn room_service:app --reload --port 8002

Exam Scheduler Service

Open another PowerShell window in the same folder and run:

$env:ROOM_SERVICE_URL="http://127.0.0.1:8002"
$env:ROOM_SERVICE_TIMEOUT="2"
$env:ROOM_SERVICE_MAX_RETRIES="3"
python -m uvicorn scheduler:app --reload --port 8003

API Documentation

- Room Booking Service: http://127.0.0.1:8002/docs
- Exam Scheduler Service: http://127.0.0.1:8003/docs
- Configuration: http://127.0.0.1:8003/config

4. Retry Test

The Room Booking Service was stopped while the Exam Scheduler was running.

The Scheduler attempted to contact the unavailable service and retried the request using exponential backoff.

Observed log:

Retry after 0.5 seconds
Retry after 1.0 seconds
Retry after 2.0 seconds
503 Service Unavailable

After restarting the Room Booking Service, requests succeeded again.

Why is retrying safe?

The booking request uses HTTP PUT with a fixed booking ID based on the exam ID.

If the same booking request is sent again with the same ID and data, the Room Booking Service returns the existing booking instead of creating a duplicate.

Therefore, retrying the request is safe.

5. Delay and Timeout Experiments

Three combinations were tested using POST "/exams".

Test| Room Delay| Timeout| Status Code| Response Time
EX004| 0 seconds| 2 seconds| 201| Very short
EX005| 1 second| 2 seconds| 201| Approximately 2 seconds
EX006| 3 seconds| 1 second| 503| Approximately 7.5 seconds

Response times are approximate observations, not exact measured timings.

Explanation

- Test 1: The service responded without delay, so the exam was booked successfully.
- Test 2: The service had a one-second delay, but the timeout was sufficient, so the booking succeeded.
- Test 3: The service delay exceeded the timeout. After several retries, the Scheduler returned 503.

This demonstrates the trade-off between timeout settings, response time, and service availability.

6. Environment Variables

The project uses environment variables for configuration:

- "ROOM_SERVICE_URL": Address of the Room Booking Service.
- "ROOM_SERVICE_TIMEOUT": Request timeout.
- "ROOM_SERVICE_MAX_RETRIES": Maximum number of retries.
- "ROOM_SERVICE_DELAY": Artificial delay in the Room Booking Service.

The "/config" endpoint displays the Scheduler configuration.