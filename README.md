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
