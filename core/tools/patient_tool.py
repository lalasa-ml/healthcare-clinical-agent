import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------
# Patient data file path resolution
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATIENTS_FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "patient_records"
    / "patients.json"
)


# ---------------------------------------------------------
# Helper: load patient database
# ---------------------------------------------------------

def _load_patient_database() -> list[dict[str, Any]]:
    if not PATIENTS_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Patient database file not found at: {PATIENTS_FILE_PATH}"
        )

    try:
        with open(PATIENTS_FILE_PATH, "r", encoding="utf-8") as file:
            patients = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError("Patient database contains invalid JSON.") from exc

    if not isinstance(patients, list):
        raise ValueError("Patient database must contain a JSON array of patient records.")

    return patients


# ---------------------------------------------------------
# Helper: validate patient records
# ---------------------------------------------------------

def _validate_patient_records(patients: list[dict[str, Any]]) -> None:
    patient_ids = set()

    for index, patient in enumerate(patients):
        if not isinstance(patient, dict):
            raise ValueError(f"Patient record at index {index} must be a JSON object.")

        patient_id = patient.get("patient_id")
        if not patient_id:
            raise ValueError(f"Patient record at index {index} does not contain a valid patient_id.")

        pid_upper = str(patient_id).strip().upper()
        if pid_upper in patient_ids:
            raise ValueError(f"Duplicate patient_id detected: {patient_id}")

        patient_ids.add(pid_upper)


# ---------------------------------------------------------
# Main patient retrieval tool
# ---------------------------------------------------------

def get_patient_record(patient_id: str) -> str:
    if patient_id is None:
        return json.dumps({"success": False, "error": "Patient ID is required."}, indent=2)

    if not isinstance(patient_id, str):
        return json.dumps({"success": False, "error": "Patient ID must be a string."}, indent=2)

    target_pid = patient_id.strip().upper()

    if not target_pid:
        return json.dumps({"success": False, "error": "Patient ID cannot be empty."}, indent=2)

    try:
        patients = _load_patient_database()
        _validate_patient_records(patients)
    except (FileNotFoundError, ValueError, OSError) as exc:
        return json.dumps({"success": False, "error": str(exc)}, indent=2)

    matching_patient = None
    for patient in patients:
        stored_id = str(patient.get("patient_id", "")).strip().upper()
        if stored_id == target_pid:
            matching_patient = patient
            break

    if matching_patient is None:
        return json.dumps(
            {
                "success": False,
                "error": f"Patient with ID '{patient_id}' was not found.",
                "patient_id": patient_id
            },
            indent=2
        )

    available_sections = []
    for section in ["demographics", "history", "medications", "recent_labs", "symptoms", "allergies"]:
        if section in matching_patient:
            available_sections.append(section)

    result = {
        "success": True,
        "patient_id": target_pid,
        "available_sections": available_sections,
        "patient_record": matching_patient
    }

    return json.dumps(result, indent=2)