import streamlit as st
import requests

# Live Azure API URL
API_BASE_URL = "https://clinical-api-backend-app.azurewebsites.net"

st.set_page_config(
    page_title="Clinical AI Support System",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Healthcare Clinical Decision Support System")
st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "💬 Physician Assistant Chat", 
    "➕ Register New Patient", 
    "📋 View Patient Directory"
])


# Helper function to fetch live patients from Azure backend API
@st.cache_data(ttl=5)
def fetch_patients_from_api():
    try:
        res = requests.get(f"{API_BASE_URL}/api/v1/patients", timeout=10)
        if res.status_code == 200:
            return res.json().get("patients", [])
        return []
    except Exception:
        return []


# =========================================================
# TAB 1: Chat Playground with Clinical Assistant
# =========================================================
with tab1:
    st.subheader("Clinical AI Assistant Chat")
    
    # Dynamically load patient IDs from Azure API
    patients_data = fetch_patients_from_api()
    patient_ids = ["None"] + [p.get("patient_id") for p in patients_data if p.get("patient_id")]

    col1, col2 = st.columns([1, 3])
    with col1:
        selected_patient = st.selectbox(
            "Select Patient Context (Optional):", 
            options=patient_ids,
            help="Select a patient ID if your question pertains to a specific record."
        )
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Clear chat button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # Display past conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input box
    if prompt := st.chat_input("Ask a clinical question (e.g., 'What medications is P-101 taking?'):"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call FastAPI Agent Endpoint
        with st.chat_message("assistant"):
            with st.spinner("Analyzing patient records & guidelines..."):
                payload = {
                    "query": prompt,
                    "patient_id": None if selected_patient == "None" else selected_patient
                }
                try:
                    res = requests.post(
                        f"{API_BASE_URL}/api/v1/agent/query", 
                        json=payload,
                        timeout=60
                    )
                    if res.status_code == 200:
                        output = res.json().get("result", "No response received.")
                    else:
                        output = f"⚠️ API Error ({res.status_code}): {res.text}"
                except Exception as e:
                    output = f"⚠️ Failed to connect to server: {str(e)}"
                
                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})


# =========================================================
# TAB 2: Dynamic Patient Entry Form for Physicians
# =========================================================
with tab2:
    st.subheader("Register a New Patient Record")
    st.info("Fill in the fields below. Submitting will automatically send the patient record to the live Azure API.")

    with st.form("patient_registration_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            p_id = st.text_input("Patient ID *", placeholder="e.g., P-106").strip().upper()
            name = st.text_input("Full Name *", placeholder="e.g., Sarah Jenkins")
        with c2:
            age = st.number_input("Age *", min_value=0, max_value=120, value=45)
            gender = st.selectbox("Gender *", ["Female", "Male", "Other"])
        with c3:
            allergies_raw = st.text_area(
                "Allergies (comma separated)", 
                placeholder="Aspirin, Iodine (Leave blank if unrecorded)"
            )
            symptoms_raw = st.text_area(
                "Symptoms (comma separated)", 
                placeholder="Blurry vision, Persistent headaches, Fatigue"
            )

        st.markdown("---")
        st.write("##### Medical History & Current Medications")
        h1, h2 = st.columns(2)
        with h1:
            history_raw = st.text_area(
                "Medical History (comma separated)", 
                placeholder="Type 2 Diabetes Mellitus, Essential Hypertension"
            )
        with h2:
            meds_raw = st.text_area(
                "Medications (Format: Name: Dosage, comma separated)", 
                placeholder="Metformin: 1000mg twice daily, Lisinopril: 10mg daily"
            )

        st.markdown("---")
        st.write("##### Recent Laboratory Results")
        l1, l2, l3 = st.columns(3)
        with l1:
            hba1c_val = st.text_input("HbA1c Value", placeholder="e.g., 9.1%")
            hba1c_date = st.date_input("HbA1c Date")
        with l2:
            egfr_val = st.text_input("eGFR Value", placeholder="e.g., 75 mL/min")
            egfr_date = st.date_input("eGFR Date")
        with l3:
            creat_val = st.text_input("Serum Creatinine Value", placeholder="e.g., 1.0 mg/dL")
            creat_date = st.date_input("Creatinine Date")

        submitted = st.form_submit_button("➕ Save Patient Record")

        if submitted:
            if not p_id or not name:
                st.error("Please fill in required fields (Patient ID and Name).")
            else:
                allergies = [a.strip() for a in allergies_raw.split(",") if a.strip()]
                symptoms = [s.strip() for s in symptoms_raw.split(",") if s.strip()]
                history = [h.strip() for h in history_raw.split(",") if h.strip()]

                medications = []
                if meds_raw:
                    for m in meds_raw.split(","):
                        if ":" in m:
                            m_name, m_dose = m.split(":", 1)
                            medications.append({"name": m_name.strip(), "dosage": m_dose.strip()})
                        elif m.strip():
                            medications.append({"name": m.strip(), "dosage": "Unspecified"})

                labs = []
                if hba1c_val:
                    try:
                        clean_num = float(hba1c_val.replace('%','').strip())
                        status_str = "High" if clean_num > 7.0 else "Normal"
                    except ValueError:
                        status_str = "Recorded"
                    labs.append({"test": "HbA1c", "value": hba1c_val, "status": status_str, "date": str(hba1c_date)})

                if egfr_val:
                    labs.append({"test": "eGFR", "value": egfr_val, "status": "Normal", "date": str(egfr_date)})
                if creat_val:
                    labs.append({"test": "Serum Creatinine", "value": creat_val, "status": "Normal", "date": str(creat_date)})

                payload = {
                    "patient_id": p_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "history": history,
                    "medications": medications,
                    "allergies": allergies,
                    "recent_labs": labs,
                    "symptoms": symptoms
                }

                # Submit to FastAPI Backend API on Azure
                try:
                    res = requests.post(f"{API_BASE_URL}/api/v1/patients/add", json=payload, timeout=15)
                    if res.status_code == 200:
                        st.success(f"✅ Patient '{p_id}' added successfully to Azure backend!")
                        st.cache_data.clear()  # Clear cache so directory and dropdown refresh immediately
                    else:
                        st.error(f"Failed to add patient: {res.json().get('detail', res.text)}")
                except Exception as exc:
                    st.error(f"Error connecting to backend server: {str(exc)}")


# =========================================================
# TAB 3: Directory View of Saved Patients
# =========================================================
with tab3:
    st.subheader("Current Patient Records Directory")

    patients_list = fetch_patients_from_api()

    if patients_list:
        for p in patients_list:
            p_id = p.get("patient_id", "Unknown")
            p_name = p.get("demographics", {}).get("name", p.get("name", "Unknown"))
            with st.expander(f"👤 Patient {p_id} - {p_name}"):
                st.json(p)
    else:
        st.info("No patient records found or unable to fetch records from backend.")