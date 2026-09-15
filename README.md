Try the app live - https://healthcare-clinical-agent-moff9v85dqrb2n8rfhhggo.streamlit.app/

# 🩺 Healthcare Clinical Support Agent
> An End-to-End Agentic AI Workspace for Physician Decision Support

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![Azure App Service](https://img.shields.io/badge/Hosting-Azure_App_Service-0089D6?style=flat&logo=microsoftazure)](https://azure.microsoft.com/)
[![Azure OpenAI](https://img.shields.io/badge/AI-Azure_OpenAI-00A4EF?style=flat&logo=openai)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

---

## 📌 Executive Summary & Problem Statement

### ❌ The Problem
When treating complex patients, physicians must manually cross-reference fragmented systems:
1. **Patient Records:** Active medications, documented drug allergies, and medical history.
2. **Laboratory Results:** Critical organ function biomarkers (e.g., eGFR, Serum Creatinine, HbA1c).
3. **Hospital Clinical Protocols:** Official dosing guidelines, contraindications, and treatment escalation thresholds.

This manual process is time-consuming and risks missing dangerous **drug-disease or drug-lab contraindications** (e.g., failing to adjust Metformin doses when kidney function drops).

### ✅ The Solution
The **Healthcare Clinical Support Agent** is a cloud-hosted, agentic AI decision-support platform. A physician can ask natural clinical questions, and the agent automatically:
* Fetches the patient's record from persistent storage.
* Cross-references biomarkers against internal hospital clinical guidelines.
* Balances therapeutic needs (e.g., escalating diabetes therapy) against safety risks (e.g., kidney failure).
* Synthesizes a structured, evidence-grounded clinical summary.

> ⚠️ **Strict Clinical Safety Rule:** The system serves purely as **Clinical Decision Support (CDS)**. It is bounded by strict guardrails and **never** autonomously prescribes medications, alters medical records, or issues definitive diagnoses.

---

## 🏗️ Architectural Overview & Data Flow

The project is built as a **decoupled, two-tier cloud architecture**:
+─────────────────────────────────────────────────────────+
|                 1. PRESENTATION LAYER                   |
|              (Streamlit Cloud UI Workspace)             |
|                                                         |
| [ Physician Chat ]  [ Add Patient ]  [ Directory View ] |
+────────────────────────────┬────────────────────────────+
                             │
                  HTTPS REST API Request
                             │
                             v
+─────────────────────────────────────────────────────────+
|                   2. BACKEND SERVICE                    |
|                (FastAPI App on Azure)                   |
|                                                         |
|  - GET /patients   : Load Directory List                |
|  - POST /add       : Validate & Store New Patient       |
|  - POST /query     : Trigger Clinical Agent Execution   |
+────────────────────────────┬────────────────────────────+
                             │
                     Executes Agent Engine
                             │
                             v
+─────────────────────────────────────────────────────────+
|              3. CLINICAL AGENT ENGINE                   |
|               (Intent & Pre-Filtering)                  |
|                                                         |
|  Step A: Regex Query Pre-Filter (_select_allowed_tools) |
|  Step B: Case-Insensitive Patient ID Extractor          |
|  Step C: Tool Call Selector & Decision Loop             |
+───────────────────┬─────────────────┬───────────────────+
                    │                 │
            Read/Write JSON      HTTP REST API Call
                    │                 │
                    v                 v
+───────────────────────+   +─────────────────────────────+
| 4. PERSISTENT STORAGE |   |     5. AI REASONING MODEL   |
| (Azure App Service)   |   |     (Azure OpenAI SDK)      |
|                       |   |                             |
| Path:                 |   |  - Select Tool Functions    |
| /home/site/wwwroot/   |   |  - Evaluate Guidelines      |
| data/patient_records/ |   |  - Synthesize Clinical      |
| patients.json         |   |    Response Payload         |
+───────────────────────+   +─────────────────────────────+

---

## 🤖 What Makes This an "Agentic AI Workflow"?

Unlike traditional single-pass LLM wrappers (which simply output text from memory), this system implements a **multi-turn reasoning & action loop**:

1. **Intent Pre-Filtering:** Analyzes the clinician's prompt via Python regex (`_select_allowed_tools`) to constrain which tool schemas (`get_patient_record`, `search_guidelines`) Azure OpenAI is allowed to see.
2. **Dynamic Tool Calling:** The model autonomously issues structured function commands (e.g., `get_patient_record(patient_id="P-108")`) without hardcoded `if/else` execution paths.
3. **Multi-Turn Loop Execution (`max_tool_rounds = 6`):** The agent reads tool outputs, determines if additional context (such as hospital guidelines) is required, and continues looping until all evidence is gathered.
4. **Multi-Patient Parallel Processing:** When asked to compare patients (e.g., `P-106` vs `P-107`), the agent issues parallel tool calls across distinct records without parameter collisions or variable overwrites.

---

## 🛡️ Clinical Safety Guardrails

* **Anti-Hallucination Controls:** The AI is strictly prohibited from inventing patient facts, symptoms, or medical history.
* **Unrecorded vs. Absent Data:** If an allergy or medical condition is missing from a record, the agent is mandated to report *"Not documented in the record"* rather than falsely claiming *"The patient has no allergies."*
* **Non-Prescriptive Boundaries:** Directly asking *"Should I prescribe drug X?"* triggers an evidence presentation (*"HbA1c is 9.4%, eGFR is 58..."*) while explicitly deferring the therapeutic decision to the licensed clinician.
* **Human-in-the-Loop (HITL):** Every output concludes with an automatic disclaimer confirming that AI responses are advisory decision-support summaries.

---

## 📂 Project Structure

healthcare-clinical-agent/
├── app/
│   ├── init.py
│   ├── api.py                  # FastAPI server, REST endpoints, persistent storage logic
│   └── main.py                 # CLI entrypoint for testing
├── core/
│   ├── init.py
│   ├── agent/
│   │   ├── init.py
│   │   └── clinical_agent.py   # Multi-tool agent loop, Azure OpenAI integration, safety rules
│   └── tools/
│       ├── init.py
│       ├── patient_tool.py     # Patient lookup tool & case-insensitive ID resolution
│       └── guidelines_tool.py  # Clinical hospital protocol lookup engine
├── data/
│   └── patient_records/
│       └── patients.json       # Persistent patient database
├── streamlit_app.py            # Multi-tab Streamlit web GUI
├── requirements.txt            # Python dependencies
├── .env                        # Local environment variables
└── README.md                   # Project documentation


---

## 🧪 Verified Test Scenarios

### Test 1: Multi-Patient Comparative Analysis
* **Prompt:** `"Compare the latest HbA1c and renal function values (eGFR) between P-106 and P-107."`
* **Result:** Agent invokes `get_patient_record("P-106")` and `get_patient_record("P-107")` in parallel, synthesizing a side-by-side comparison of P-106 (Sarah Jenkins: HbA1c 9.1%, eGFR 75) vs P-107 (Elena Rostova: HbA1c 8.9%, eGFR 72).

### Test 2: Multi-Variable Safety Evaluation
* **Prompt:** `"P-108 has an HbA1c of 9.4% and eGFR of 58 mL/min. What do hospital guidelines recommend regarding his Metformin dosage and treatment escalation?"`
* **Result:** 
  * Identifies eGFR of 58 mL/min is safely above the < 45 mL/min dose reduction threshold (recommending Metformin continuation).
  * Identifies HbA1c of 9.4% exceeds the > 8.0% trigger, recommending dual-therapy escalation consideration (e.g., SGLT2 inhibitor or GLP-1 RA).
  * Flags P-108's Congestive Heart Failure history as a critical factor for physician review.

---

## 🚀 Deployment Instructions

### 1. Azure App Service Backend
```cmd
:: Create App Service Plan & Web App
az appservice plan create --name clinical-api-plan --resource-group HealthcareApp-RG --sku B1 --is-linux
az webapp create --name clinical-api-backend-app --resource-group HealthcareApp-RG --plan clinical-api-plan --runtime "PYTHON:3.12"

:: Configure Startup Command & Settings
az webapp config set --resource-group HealthcareApp-RG --name clinical-api-backend-app --startup-file "gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.api:app"
az webapp config set --resource-group HealthcareApp-RG --name clinical-api-backend-app --always-on true

:: Set Azure OpenAI Credentials
az webapp config appsettings set --resource-group HealthcareApp-RG --name clinical-api-backend-app --settings AZURE_OPENAI_API_KEY="YOUR_KEY" AZURE_OPENAI_ENDPOINT="https://YOUR_[RESOURCE.openai.azure.com/](https://RESOURCE.openai.azure.com/)" AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4.1-mini" AZURE_OPENAI_API_VERSION="2024-08-01-preview"

:: Push Code to Azure
git push azure main
2. Streamlit Cloud Frontend
Push repository to GitHub (git push origin main).

Log into share.streamlit.io, connect your GitHub repository, set entrypoint to streamlit_app.py, and deploy!

🛠️ Tech Stack & Dependencies
Language: Python 3.12

Backend Framework: FastAPI, Uvicorn, Gunicorn, Pydantic

Frontend Framework: Streamlit

AI & Orchestration: Azure OpenAI SDK (gpt-4.1-mini / gpt-4o), Tool Calling Schema, Python re module

Cloud Hosting: Azure App Service (Linux Web App), Streamlit Community Cloud

Data Persistence: JSON / Azure Persistent Disk Mapping (/home/site/wwwroot/data/...)
