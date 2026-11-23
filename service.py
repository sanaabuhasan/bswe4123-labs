from fastapi import FastAPI
import time

app = FastAPI()

start_time = time.time()


@app.get("/")
def home():
    return {"message": "Service is running"}


@app.get("/health")
def health(delay: float = 0.0):
    if delay > 0:
        time.sleep(delay)

    uptime = time.time() - start_time

    return {
        "status": "ok",
        "uptime": uptime
    }