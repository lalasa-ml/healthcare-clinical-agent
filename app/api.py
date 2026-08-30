import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.agent.clinical_agent import ClinicalAgent

app = FastAPI(title="Clinical Support Agent API")
agent = ClinicalAgent()

# Absolute path resolution ensuring reliability across local and containerized environments
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATIENTS_FILE = os.path.join(BASE_DIR, "data", "patient_records", "patients.json")


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
# Endpoints
# ---------------------------------------------------------

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
        patients = []
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(PATIENTS_FILE), exist_ok=True)

        if os.path.exists(PATIENTS_FILE):
            with open(PATIENTS_FILE, "r") as f:
                patients = json.load(f)

        # Check for duplicate Patient ID
        for p in patients:
            if p.get("patient_id", "").upper() == patient.patient_id.upper():
                raise HTTPException(
                    status_code=400, 
                    detail=f"Patient ID '{patient.patient_id}' already exists!"
                )

        # Format new patient entry using Pydantic V2 model_dump()
        new_patient = {
            "patient_id": patient.patient_id.upper(),
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

        # Write back updated patient array to patients.json
        with open(PATIENTS_FILE, "w") as f:
            json.dump(patients, f, indent=2)

        return {
            "status": "success",
            "message": f"Patient {patient.patient_id.upper()} added successfully!"
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))