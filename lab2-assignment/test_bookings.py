import httpx

BASE_URL = "http://127.0.0.1:8001"

client = httpx.Client()


def show_response(description, response):
    print(f"{description}: {response.status_code}")
    if response.content:
        print(response.json())


# 1. Create a room
room = {
    "id": "B205",
    "building": "Engineering",
    "capacity": 30
}

response = client.post(f"{BASE_URL}/rooms", json=room)
show_response("Create room", response)


# 2. Try creating the same room again (409)
response = client.post(f"{BASE_URL}/rooms", json=room)
show_response("Duplicate room", response)


# 3. Get all rooms
response = client.get(f"{BASE_URL}/rooms")
show_response("Get all rooms", response)


# 4. Get an existing room
response = client.get(f"{BASE_URL}/rooms/B205")
show_response("Get existing room", response)


# 5. Get an unknown room (404)
response = client.get(f"{BASE_URL}/rooms/UNKNOWN")
show_response("Get unknown room", response)


# 6. Create a valid booking (201)
booking = {
    "room_id": "B205",
    "day": "2026-12-01",
    "start_hour": 10,
    "end_hour": 12,
    "purpose": "Study group"
}

response = client.put(
    f"{BASE_URL}/bookings/BK001",
    json=booking
)
show_response("Create booking", response)


# 7. Retry the same booking (200)
response = client.put(
    f"{BASE_URL}/bookings/BK001",
    json=booking
)
show_response("Retry same booking", response)


# 8. Same booking ID with different data (409)
different_booking = {
    "room_id": "B205",
    "day": "2026-12-01",
    "start_hour": 10,
    "end_hour": 12,
    "purpose": "Meeting"
}

response = client.put(
    f"{BASE_URL}/bookings/BK001",
    json=different_booking
)
show_response("Same ID with different data", response)


# 9. Try an overlapping booking (409)
overlapping_booking = {
    "room_id": "B205",
    "day": "2026-12-01",
    "start_hour": 11,
    "end_hour": 13,
    "purpose": "Meeting"
}

response = client.put(
    f"{BASE_URL}/bookings/BK002",
    json=overlapping_booking
)
show_response("Overlapping booking", response)


# 10. Adjacent booking is allowed (201)
adjacent_booking = {
    "room_id": "B205",
    "day": "2026-12-01",
    "start_hour": 12,
    "end_hour": 13,
    "purpose": "Another study group"
}

response = client.put(
    f"{BASE_URL}/bookings/BK003",
    json=adjacent_booking
)
show_response("Adjacent booking", response)


# 11. Try an invalid booking (422)
invalid_booking = {
    "room_id": "B205",
    "day": "2026-12-01",
    "start_hour": 15,
    "end_hour": 10,
    "purpose": "Invalid time"
}

response = client.put(
    f"{BASE_URL}/bookings/BK004",
    json=invalid_booking
)
show_response("Invalid booking hours", response)


# 12. Try booking an unknown room (404)
unknown_room_booking = {
    "room_id": "UNKNOWN",
    "day": "2026-12-01",
    "start_hour": 14,
    "end_hour": 15,
    "purpose": "Study"
}

response = client.put(
    f"{BASE_URL}/bookings/BK005",
    json=unknown_room_booking
)
show_response("Booking unknown room", response)


# 13. Get existing booking
response = client.get(f"{BASE_URL}/bookings/BK001")
show_response("Get booking", response)


# 14. Get unknown booking (404)
response = client.get(f"{BASE_URL}/bookings/UNKNOWN")
show_response("Get unknown booking", response)


# 15. Delete booking (204)
response = client.delete(f"{BASE_URL}/bookings/BK001")
show_response("Delete booking", response)


# 16. Delete the same booking again (404)
response = client.delete(f"{BASE_URL}/bookings/BK001")
show_response("Delete unknown booking", response)


# 17. Delete adjacent booking (204)
response = client.delete(f"{BASE_URL}/bookings/BK003")
show_response("Delete adjacent booking", response)


client.close()