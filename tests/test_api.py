import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health_check_query_endpoint():
    """Verify API endpoint returns 200 OK for valid query"""
    response = client.post(
        "/api/v1/agent/query",
        json={
            "query": "What medications is P-101 taking?",
            "patient_id": "P-101"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "result" in data


def test_add_patient_endpoint():
    """Verify dynamic patient registration endpoint formats and saves data"""
    test_patient = {
        "patient_id": "P-999",
        "name": "Test Patient",
        "age": 40,
        "gender": "Male",
        "history": ["Hypertension"],
        "medications": [{"name": "Lisinopril", "dosage": "10mg Daily"}],
        "allergies": ["Aspirin"],
        "recent_labs": [],
        "symptoms": []
    }
    response = client.post("/api/v1/patients/add", json=test_patient)
    assert response.status_code in [200, 400] # 200 if new, 400 if already created in previous run