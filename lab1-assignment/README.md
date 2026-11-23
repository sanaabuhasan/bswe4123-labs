Lab Assignment 1: Is the Service Up, Slow or Down?

1. Health Endpoint

The FastAPI service provides a "/health" endpoint that returns the service status and uptime in seconds.

An optional delay parameter was added to simulate slow responses.

2. Three Service Instances

The service was run on three different ports:

- Service 1: 8001
- Service 2: 8002
- Service 3: 8003

3. Monitoring Results

The monitor checks the three services every 2 seconds using HTTPX.

- UP: Response time is 500 ms or less.
- SLOW: Response time is more than 500 ms.
- DOWN: The service fails three consecutive checks.

Example output:

--- Health Check ---
Service 1: UP
Service 2: SLOW
Service 3: UP

When Service 3 was stopped, the monitor showed:

Service 3: Check failed (1/3)
Service 3: Check failed (2/3)
Service 3: DOWN

After restarting Service 3, its status returned to UP.

4. Failure Threshold

A single failed check does not mean that the service is down. The monitor waits for three consecutive failures before reporting DOWN. A successful check resets the failure counter.

5. Timeout and Trade-offs

The timeout is set to 2 seconds to prevent waiting indefinitely.

Three consecutive failures help reduce false alarms. However, this means detecting a real failure takes longer. A shorter timeout detects failures faster but may cause false alarms, while a longer timeout delays failure detection.