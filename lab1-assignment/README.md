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
## One-Minute Monitoring Test

The monitor was run for approximately one minute while all three services were active.

The results showed:

- Service 1: UP
- Service 2: SLOW
- Service 3: UP

Service 2 was intentionally configured with a 0.8-second delay. Therefore, its response time was greater than 500 ms and the monitor correctly classified it as SLOW.

The monitor completed approximately 21 health-check cycles during the test.

This test confirms that the monitoring system can identify healthy and slow services.
Actual Monitoring Output

One-Minute Monitoring Test

The following output was observed during the one-minute test:

--- Health Check ---
Service 1: UP (198.9 ms)
Service 2: SLOW (873.8 ms)
Service 3: UP (94.8 ms)

--- Health Check ---
Service 1: UP (29.6 ms)
Service 2: SLOW (835.0 ms)
Service 3: UP (28.4 ms)

--- Health Check ---
Service 1: UP (25.9 ms)
Service 2: SLOW (829.9 ms)
Service 3: UP (25.5 ms)

--- Health Check ---
Service 1: UP (31.6 ms)
Service 2: SLOW (833.7 ms)
Service 3: UP (47.0 ms)

The monitor completed approximately 21 monitoring rounds. Service 1 and Service 3 remained UP, while Service 2 remained SLOW because of the intentional 0.8-second delay.

Stopping and Restarting a Service

When Service 3 was stopped, the monitor detected consecutive failures:

Service 3: Check failed (1/3)
Service 3: Check failed (2/3)
Service 3: DOWN

After Service 3 was restarted, its status returned to UP.

This demonstrates that the monitor can detect service failures and recovery.