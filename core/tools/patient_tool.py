import json
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# Patient data file
# ---------------------------------------------------------

# Resolve the project root based on this Python file rather
# than depending on the directory from which the program
# happens to be executed.
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
    """
    Loads the patient records from the JSON file.

    Returns:
        A list containing patient dictionaries.

    Raises:
        FileNotFoundError:
            If the patient JSON file does not exist.

        ValueError:
            If the JSON structure is invalid.
    """

    if not PATIENTS_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Patient database file not found at: "
            f"{PATIENTS_FILE_PATH}"
        )

    try:

        with open(
            PATIENTS_FILE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            patients = json.load(file)

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Patient database contains invalid JSON."
        ) from exc

    if not isinstance(patients, list):

        raise ValueError(
            "Patient database must contain a JSON array "
            "of patient records."
        )

    return patients


# ---------------------------------------------------------
# Helper: validate patient records
# ---------------------------------------------------------

def _validate_patient_records(
    patients: list[dict[str, Any]]
) -> None:
    """
    Validates the basic structure of patient records.

    This does not enforce a rigid medical schema because
    the application should remain flexible enough to support
    different types of patient information.
    """

    patient_ids = set()

    for index, patient in enumerate(patients):

        if not isinstance(patient, dict):

            raise ValueError(
                f"Patient record at index {index} "
                "must be a JSON object."
            )

        patient_id = patient.get("patient_id")

        if not patient_id:

            raise ValueError(
                f"Patient record at index {index} "
                "does not contain a valid patient_id."
            )

        if patient_id in patient_ids:

            raise ValueError(
                f"Duplicate patient_id detected: "
                f"{patient_id}"
            )

        patient_ids.add(patient_id)


# ---------------------------------------------------------
# Main patient retrieval tool
# ---------------------------------------------------------

def get_patient_record(patient_id: str) -> str:
    """
    Retrieves a patient record using the patient ID.

    This function is designed to be used as an agent tool.

    Args:
        patient_id:
            Unique patient identifier such as P-101.

    Returns:
        A JSON string containing either:

        - the requested patient record
        - a safe error response
    """

    # -----------------------------------------------------
    # STEP 1: Validate input
    # -----------------------------------------------------

    if patient_id is None:

        return json.dumps(
            {
                "success": False,
                "error": "Patient ID is required."
            },
            indent=2
        )

    if not isinstance(patient_id, str):

        return json.dumps(
            {
                "success": False,
                "error": "Patient ID must be a string."
            },
            indent=2
        )

    patient_id = patient_id.strip()

    if not patient_id:

        return json.dumps(
            {
                "success": False,
                "error": "Patient ID cannot be empty."
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 2: Load patient database
    # -----------------------------------------------------

    try:

        patients = _load_patient_database()

    except FileNotFoundError as exc:

        return json.dumps(
            {
                "success": False,
                "error": str(exc)
            },
            indent=2
        )

    except ValueError as exc:

        return json.dumps(
            {
                "success": False,
                "error": str(exc)
            },
            indent=2
        )

    except OSError as exc:

        return json.dumps(
            {
                "success": False,
                "error": (
                    "Unable to access patient database: "
                    f"{str(exc)}"
                )
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 3: Validate database structure
    # -----------------------------------------------------

    try:

        _validate_patient_records(patients)

    except ValueError as exc:

        return json.dumps(
            {
                "success": False,
                "error": str(exc)
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 4: Search for requested patient
    # -----------------------------------------------------

    matching_patient = None

    for patient in patients:

        stored_patient_id = str(
            patient.get("patient_id", "")
        ).strip()

        if stored_patient_id == patient_id:

            matching_patient = patient

            break

    # -----------------------------------------------------
    # STEP 5: Handle unknown patient
    # -----------------------------------------------------

    if matching_patient is None:

        return json.dumps(
            {
                "success": False,
                "error": (
                    f"Patient with ID '{patient_id}' "
                    "was not found."
                ),
                "patient_id": patient_id
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 6: Determine available information
    # -----------------------------------------------------

    available_sections = []

    if "demographics" in matching_patient:
        available_sections.append("demographics")

    if "history" in matching_patient:
        available_sections.append("history")

    if "medications" in matching_patient:
        available_sections.append("medications")

    if "recent_labs" in matching_patient:
        available_sections.append("recent_labs")

    # -----------------------------------------------------
    # STEP 7: Return structured tool result
    # -----------------------------------------------------

    result = {
        "success": True,
        "patient_id": patient_id,
        "available_sections": available_sections,
        "patient_record": matching_patient
    }

    return json.dumps(
        result,
        indent=2
    )