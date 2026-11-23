import time
import httpx

services = {
    "Service 1": "http://127.0.0.1:8001/health",
    "Service 2": "http://127.0.0.1:8002/health?delay=0.8",
    "Service 3": "http://127.0.0.1:8003/health"
}

# Count consecutive failures for each service
failure_counts = {
    name: 0 for name in services
}

MAX_FAILURES = 3

while True:
    print("\n--- Health Check ---")

    for name, url in services.items():
        start = time.perf_counter()

        try:
            response = httpx.get(url, timeout=2.0)
            response.raise_for_status()

            elapsed = (time.perf_counter() - start) * 1000

            # Reset failures after a successful response
            failure_counts[name] = 0

            if elapsed > 500:
                print(f"{name}: SLOW ({elapsed:.1f} ms)")
            else:
                print(f"{name}: UP ({elapsed:.1f} ms)")

        except (httpx.RequestError, httpx.HTTPStatusError):
            failure_counts[name] += 1

            if failure_counts[name] >= MAX_FAILURES:
                print(f"{name}: DOWN")
            else:
                print(
                    f"{name}: Check failed "
                    f"({failure_counts[name]}/{MAX_FAILURES})"
                )

    time.sleep(2)