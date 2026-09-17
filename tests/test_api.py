import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["DEVICE_SYSTEMS_DB_URL"] = "sqlite:///./test_device_systems.db"

from app.database.connection import Base, engine
from app.main import app

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

client = TestClient(app)


def test_create_user_and_device_and_loan_flow():
    user_payload = {"name": "Ana Pérez", "email": "ana@sena.edu.co", "phone": "3001234567"}
    user_response = client.post("/users", json=user_payload)
    assert user_response.status_code == 201, user_response.text
    user_data = user_response.json()
    assert user_data["email"] == user_payload["email"]

    device_payload = {
        "name": "Laptop Lenovo ThinkPad",
        "serial_number": "LEN-2024-001",
        "device_type": "laptop",
        "brand": "Lenovo",
        "is_available": True,
    }
    device_response = client.post("/devices", json=device_payload)
    assert device_response.status_code == 201, device_response.text
    device_data = device_response.json()
    assert device_data["serial_number"] == device_payload["serial_number"]

    loan_payload = {"user_id": user_data["id"], "device_id": device_data["id"], "status": "active"}
    loan_response = client.post("/loans", json=loan_payload)
    assert loan_response.status_code == 201, loan_response.text
    loan_data = loan_response.json()
    assert loan_data["status"] == "active"

    loan_detail = client.get(f"/loans/{loan_data['id']}/details")
    assert loan_detail.status_code == 200, loan_detail.text
    detail = loan_detail.json()
    assert detail["user"]["email"] == user_payload["email"]
    assert detail["device"]["serial_number"] == device_payload["serial_number"]

    return_response = client.patch(f"/loans/{loan_data['id']}/return")
    assert return_response.status_code == 200, return_response.text
    assert return_response.json()["status"] == "returned"

    device_after_return = client.get(f"/devices/{device_data['id']}")
    assert device_after_return.status_code == 200, device_after_return.text
    assert device_after_return.json()["is_available"] is True


def test_list_loans_filtered_by_status_and_device_type():
    user_response = client.post("/users", json={"name": "Carlos", "email": "carlos@sena.edu.co", "phone": "3001234568"})
    user_id = user_response.json()["id"]

    device_response = client.post(
        "/devices",
        json={
            "name": "Tablet Samsung",
            "serial_number": "SAM-2024-001",
            "device_type": "tablet",
            "brand": "Samsung",
            "is_available": True,
        },
    )
    device_id = device_response.json()["id"]

    client.post("/loans", json={"user_id": user_id, "device_id": device_id, "status": "active"})

    active_loans = client.get("/loans", params={"status": "active"})
    assert active_loans.status_code == 200, active_loans.text
    assert any(item["status"] == "active" for item in active_loans.json())

    device_type_loans = client.get("/loans", params={"device_type": "tablet"})
    assert device_type_loans.status_code == 200, device_type_loans.text
    assert any(item["device"]["device_type"] == "tablet" for item in device_type_loans.json())


def test_business_errors_history_and_date_filters():
    user_response = client.post(
        "/users",
        json={"name": "Laura", "email": "laura@sena.edu.co", "phone": "3001234569"},
    )
    user_id = user_response.json()["id"]
    device_payload = {
        "name": "Monitor Dell",
        "serial_number": "DEL-2024-001",
        "device_type": "monitor",
        "brand": "Dell",
        "is_available": True,
    }
    device_response = client.post("/devices", json=device_payload)
    device_id = device_response.json()["id"]

    duplicate_device = client.post("/devices", json=device_payload)
    assert duplicate_device.status_code == 400

    invalid_status = client.post(
        "/loans", json={"user_id": user_id, "device_id": device_id, "status": "invalid"}
    )
    assert invalid_status.status_code == 422

    loan_response = client.post("/loans", json={"user_id": user_id, "device_id": device_id})
    loan_id = loan_response.json()["id"]

    unavailable_device = client.post("/loans", json={"user_id": user_id, "device_id": device_id})
    assert unavailable_device.status_code == 409

    user_history = client.get(f"/users/{user_id}/loans")
    device_history = client.get(f"/devices/{device_id}/loans")
    assert user_history.status_code == 200
    assert device_history.status_code == 200
    assert user_history.json()[0]["id"] == loan_id
    assert device_history.json()[0]["id"] == loan_id

    email_filter = client.get("/loans", params={"user_email": "laura@sena.edu.co"})
    future_filter = client.get("/loans", params={"loan_date_from": "2099-01-01T00:00:00"})
    assert email_filter.status_code == 200
    assert len(email_filter.json()) == 1
    assert future_filter.status_code == 200
    assert future_filter.json() == []

    return_response = client.patch(f"/loans/{loan_id}/return")
    second_return = client.patch(f"/loans/{loan_id}/return")
    assert return_response.status_code == 200
    assert second_return.status_code == 409

    invalid_filter = client.get("/loans", params={"status": "invalid"})
    assert invalid_filter.status_code == 422


def test_put_requires_complete_payload():
    user_response = client.post(
        "/users", json={"name": "Mario", "email": "mario@sena.edu.co"}
    )
    user_id = user_response.json()["id"]
    incomplete_user = client.put(f"/users/{user_id}", json={"name": "Mario Nuevo"})
    assert incomplete_user.status_code == 422

    complete_user = client.put(
        f"/users/{user_id}",
        json={"name": "Mario Nuevo", "email": "mario.nuevo@sena.edu.co", "phone": None, "is_active": True},
    )
    assert complete_user.status_code == 200
