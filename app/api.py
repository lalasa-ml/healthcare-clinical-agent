import json
import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.agent.clinical_agent import ClinicalAgent

app = FastAPI(title="Clinical Support Agent API")
agent = ClinicalAgent()

# Dynamic path resolution: use persistent Azure App Service path if deployed
if os.getenv("HOME") and Path("/home/site/wwwroot").exists():
    PATIENTS_FILE = Path("/home/site/wwwroot/data/patient_records/patients.json")
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    PATIENTS_FILE = PROJECT_ROOT / "data" / "patient_records" / "patients.json"


# ---------------------------------------------------------
# Pydantic Schemas for Requests
# ---------------------------------------------------------

class MedicationItem(BaseModel):
    name: str
    dosage: str

class LabItem(BaseModel):
    test: str
    value: str
    status: Optional[str] = "Normal"
    date: str

class PatientCreateRequest(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    history: List[str] = []
    medications: List[MedicationItem] = []
    allergies: List[str] = []
    recent_labs: List[LabItem] = []
    symptoms: List[str] = []

class QueryRequest(BaseModel):
    patient_id: Optional[str] = None
    query: str


# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def load_patients_from_file() -> list:
    if not PATIENTS_FILE.exists():
        return []
    try:
        with open(PATIENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_patients_to_file(patients: list) -> None:
    PATIENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2)


# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------

@app.get("/api/v1/patients")
def get_all_patients():
    """Retrieve all patients for the Streamlit directory view."""
    try:
        patients = load_patients_from_file()
        return {"status": "success", "count": len(patients), "patients": patients}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/agent/query")
def run_agent_query(request: QueryRequest):
    try:
        response_text = agent.run_offline_loop(
            user_query=request.query,
            patient_id=request.patient_id
        )
        return {
            "status": "success",
            "patient_id": request.patient_id,
            "result": response_text
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/v1/patients/add")
def add_patient(patient: PatientCreateRequest):
    try:
        patients = load_patients_from_file()
        pid = patient.patient_id.strip().upper()

        # Check for duplicate Patient ID
        for p in patients:
            if str(p.get("patient_id", "")).strip().upper() == pid:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Patient ID '{pid}' already exists!"
                )

        # Format new patient entry
        new_patient = {
            "patient_id": pid,
            "demographics": {
                "name": patient.name,
                "age": patient.age,
                "gender": patient.gender
            },
            "history": patient.history,
            "medications": [m.model_dump() for m in patient.medications],
            "allergies": patient.allergies,
            "recent_labs": [l.model_dump() for l in patient.recent_labs],
            "symptoms": patient.symptoms
        }

        patients.append(new_patient)
        save_patients_to_file(patients)

        return {
            "status": "success",
            "message": f"Patient {pid} added successfully!"
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))