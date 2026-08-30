from core.tools.patient_tool import get_patient_record
from core.tools.guidelines_tool import search_clinical_guidelines

def test_tools():
    print("=== Testing Patient Tool ===")
    patient_result = get_patient_record("P-101")
    print(patient_result)
    
    print("\n=== Testing Guidelines Tool ===")
    guideline_result = search_clinical_guidelines("Metformin")
    print(guideline_result)

if __name__ == "__main__":
    test_tools()