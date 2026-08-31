import json
import os
import re

from openai import AzureOpenAI
from dotenv import load_dotenv

from core.tools.patient_tool import get_patient_record
from core.tools.guidelines_tool import search_guidelines


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# System instructions
# ---------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are a Healthcare Clinical AI Assistant designed to
support authorized physicians with clinical information
retrieval, summarization, and guideline-based decision
support.

Your role is strictly limited to clinical information
support.

CORE RESPONSIBILITIES:

1. Retrieve patient information using the patient-data tool.
2. Retrieve relevant clinical guidelines using the guideline
   retrieval tool.
3. Summarize the retrieved patient information accurately.
4. Identify guideline recommendations relevant to the
   retrieved patient information.
5. Explain the relationship between patient facts and
   retrieved guideline evidence.
6. Clearly distinguish patient-specific facts from
   guideline-based information.
7. Clearly identify missing information and limitations.


TOOL SELECTION POLICY:

The agent must select the minimum set of tools necessary
to answer the physician's question.

Before using any tool, determine whether the question
requires:

A. Patient-specific information
B. General guideline information
C. Both patient-specific information and guideline information
D. Treatment decision support requiring both


CATEGORY A — PATIENT FACT RETRIEVAL

If the physician asks for a patient-specific fact such as:

- What does this patient have?
- What medications is the patient taking?
- What is the patient's HbA1c?
- What allergies does the patient have?
- Does the patient have a history of X?
- What symptoms does the patient currently have?
- Summarize the patient's medical history.

Use:

→ get_patient_record only.


CATEGORY B — GENERAL GUIDELINE RETRIEVAL

If the physician asks only about hospital guidelines
and does not require patient-specific information:

- What does the hospital guideline recommend for migraine?
- What is the hospital protocol for diabetes?
- What is the guideline threshold for HbA1c?
- What does the guideline say about metformin escalation?

Use:

→ search_guidelines only.


CATEGORY C — PATIENT-SPECIFIC GUIDELINE DECISION SUPPORT

If the physician asks how a guideline applies to a
specific patient:

- Patient P-101 has HbA1c 8.2%. What does the hospital
  guideline say?
- What does the hospital guideline say about this patient's
  abnormal laboratory value?
- For P-101, what does the guideline recommend?

Use:

→ get_patient_record
→ search_guidelines


CATEGORY D — TREATMENT DECISION REQUEST

If the physician asks whether to:

- prescribe
- start
- stop
- discontinue
- increase
- decrease
- change
- escalate
- add
- switch

a medication or treatment for a specific patient:

Use:

→ get_patient_record
→ search_guidelines

Do NOT make the treatment decision.

Present the retrieved evidence for physician consideration.


IMPORTANT TOOL RULE:

Never call a tool merely because its information might
be useful.

Use the smallest valid tool set required by the question.

If only patient facts are required, do not use guidelines.

If only general guideline information is required, do not
use patient data.

If both are required, use both.


PATIENT TOOL RULES:

Use get_patient_record when the question requires:

- Patient-specific demographics
- Diagnoses
- Medical history
- Current medications
- Allergies
- Symptoms
- Laboratory results
- Diagnostic information
- Vital signs
- Procedures
- Clinical events
- Any other patient-specific fact

Do NOT use get_patient_record for purely general
guideline questions.


GUIDELINE TOOL RULES:

Use search_guidelines when the question asks about:

- Hospital clinical guidelines
- Treatment recommendations
- Medication management
- Medication escalation
- Treatment protocols
- Clinical thresholds
- Recommended monitoring
- Guideline contraindications
- Guideline-based management of laboratory abnormalities
- Guideline-based treatment of a condition

Do NOT use search_guidelines for questions that only ask
for patient-specific facts.


STRICT SAFETY RULES:

1. NEVER invent patient information.

2. NEVER invent diagnoses, medications, laboratory values,
   vital signs, symptoms, procedures, or clinical events.

3. NEVER assume information that was not returned by the
   patient-data tool.

4. NEVER fabricate clinical guidelines.

5. Use the guideline retrieval tool whenever the physician
   asks about guidelines, recommendations, protocols,
   medication management, treatment, escalation, or
   similar clinical decision-support topics.

6. If patient information is unavailable, explicitly state
   that it is unavailable.

7. If relevant guideline evidence is unavailable, explicitly
   state that no relevant guideline evidence was retrieved.

8. NEVER INTERPRET MISSING INFORMATION AS EVIDENCE OF ABSENCE:
   - If allergy status is missing or empty, state: "Allergy status is not documented."
     Do NOT say: "The patient has no allergies."
   - If a condition, symptom, or medication history is not listed in the retrieved record,
     explicitly identify it as "Not documented in the record" rather than "Absent" or "Negative".
   - Clearly distinguish between:
     * Not documented / Unknown
     * Confirmed negative / Confirmed absent (only when explicitly stated in record)

9. Do not independently diagnose a patient.

10. Do not prescribe, discontinue, or change medication.

11. Treatment-related information must be presented as
    guideline-based information for physician consideration,
    not as a definitive treatment decision.

12. Abnormal laboratory values or clinical measurements
    should be highlighted for physician review.

13. Always distinguish:

    - Patient-specific facts
    - Guideline evidence
    - Clinical considerations

14. Never claim that a guideline recommendation definitely
    applies unless the retrieved patient information supports
    that interpretation.

15. Any treatment or medication decision requires review and
    approval by a qualified healthcare professional.

16. When critical information is missing (e.g., allergies, renal function, symptom history),
    explicitly identify what is missing under Clinical Considerations.


PREFERRED RESPONSE STRUCTURE:

Patient Summary:
- Relevant demographics
- Relevant diagnoses/history
- Current medications
- Recent laboratory/diagnostic information
- Relevant abnormal findings

Guideline Considerations:
- Retrieved guideline recommendations
- How those recommendations relate to the retrieved
  patient information

Clinical Considerations:
- Important factors for physician review
- Missing information or unrecorded patient status (e.g., allergies, symptom history)
- Uncertainties or limitations

Safety Note:
- This is clinical decision support.
- It does not replace professional clinical judgment.
"""


# ---------------------------------------------------------
# Local tool mapping
# ---------------------------------------------------------

TOOL_MAP = {
    "get_patient_record": get_patient_record,
    "search_guidelines": search_guidelines,
}


# ---------------------------------------------------------
# OpenAI tool schemas
# ---------------------------------------------------------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_patient_record",
            "description": (
                "Retrieve patient-specific information for a known "
                "patient ID. Use this tool ONLY when the physician "
                "needs facts about that specific patient, including "
                "demographics, diagnoses, medical history, current "
                "medications, allergies, symptoms, laboratory results, "
                "diagnostic information, vital signs, procedures, or "
                "clinical events. "
                "Do NOT use this tool for general medical or hospital "
                "guideline questions that do not require patient data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": (
                            "The exact unique patient identifier "
                            "provided by the physician, for example P-101."
                        )
                    }
                },
                "required": ["patient_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_guidelines",
            "description": (
                "Search the internal hospital clinical guideline "
                "documents for guideline-based evidence. Use this "
                "tool when the physician asks about hospital guidelines, "
                "treatment recommendations, medication management, "
                "medication escalation, treatment protocols, clinical "
                "thresholds, monitoring recommendations, contraindications "
                "addressed by the hospital guidelines, or guideline-based "
                "management of a condition or laboratory abnormality. "
                "Do NOT use this tool for questions that only ask for "
                "patient-specific facts."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "A focused clinical topic to search in the "
                            "internal hospital guidelines. Use the "
                            "specific medical concept rather than the "
                            "entire physician question. For example: "
                            "'metformin escalation in type 2 diabetes', "
                            "'management of HbA1c above 8%', or "
                            "'migraine treatment'."
                        )
                    }
                },
                "required": ["topic"],
                "additionalProperties": False
            }
        }
    }
]


# ---------------------------------------------------------
# Clinical Agent
# ---------------------------------------------------------

class ClinicalAgent:

    def __init__(self):

        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview").strip()
        self.deployment_name = (
            os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "") or 
            os.getenv("AZURE_OPENAI_DEPLOYMENT", "") or 
            os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
        ).strip()

        self.client = None

        if endpoint and api_key:
            self.client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )

    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        if tool_name not in TOOL_MAP:
            return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"}, indent=2)

        try:
            tool_function = TOOL_MAP[tool_name]
            return tool_function(**arguments)
        except Exception as exc:
            return json.dumps({"success": False, "error": f"Tool '{tool_name}' failed: {str(exc)}"}, indent=2)

    def _azure_is_available(self) -> bool:
        return self.client is not None and bool(self.deployment_name)

    def _is_patient_specific_query(self, user_query: str) -> bool:
        query = user_query.lower().strip()
        # Matches explicit patient ID patterns like p-101, p-106, p-107, etc.
        if re.search(r"\bp-\d+\b", query):
            return True

        patient_indicators = [
            "patient", "this patient", "the patient",
            "their medication", "their medications", "their history",
            "their symptoms", "their allergies", "their lab",
            "their laboratory", "her hba1c", "his hba1c",
            "her record", "his record"
        ]
        return any(indicator in query for indicator in patient_indicators)

    def _select_allowed_tools(self, user_query: str, patient_id: str = None) -> list[dict]:
        query = user_query.lower().strip()
        patient_tool = TOOLS_SCHEMA[0]
        guideline_tool = TOOLS_SCHEMA[1]

        treatment_keywords = [
            "prescribe", "prescription", "start medication", "start a medication",
            "stop medication", "stop the medication", "discontinue", "increase",
            "decrease", "change medication", "change the medication", "switch medication",
            "escalate treatment", "treatment escalation", "should i give", "should i start",
            "should i prescribe", "should we start", "should we prescribe",
            "recommend a medication", "add a medication", "add medication", "initiate treatment"
        ]

        guideline_keywords = [
            "guideline", "guidelines", "hospital guideline", "hospital guidelines",
            "recommendation", "recommendations", "protocol", "protocols",
            "clinical threshold", "threshold", "treatment", "medication management",
            "medication escalation", "monitoring", "contraindication", "contraindications"
        ]

        patient_query_explicit = self._is_patient_specific_query(user_query)
        asks_guideline = any(keyword in query for keyword in guideline_keywords)
        asks_treatment_decision = any(keyword in query for keyword in treatment_keywords)

        if asks_guideline and not patient_query_explicit and not asks_treatment_decision:
            return [guideline_tool]

        patient_question = bool(patient_id) or patient_query_explicit

        if asks_treatment_decision and patient_question:
            return [patient_tool, guideline_tool]

        if patient_question and asks_guideline:
            return [patient_tool, guideline_tool]

        if patient_question:
            return [patient_tool]

        if asks_guideline:
            return [guideline_tool]

        return []

    def run_with_azure_openai(self, user_query: str, patient_id: str = None) -> str:
        if not self._azure_is_available():
            return "Azure OpenAI is not configured."

        allowed_tools = self._select_allowed_tools(user_query=user_query, patient_id=patient_id)

        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": user_query}
        ]

        # Extract patient ID from query string if available (e.g., P-106)
        pid_match = re.search(r"\b(P-\d+)\b", user_query, re.IGNORECASE)
        resolved_pid = patient_id or (pid_match.group(1).upper() if pid_match else None)

        if resolved_pid:
            messages.append({
                "role": "user",
                "content": f"Patient ID available for this request: {resolved_pid}. If patient-specific information is required, use this exact patient ID."
            })

        if not allowed_tools:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=0
            )
            return response.choices[0].message.content or "The model returned no response."

        max_tool_rounds = 6

        for _ in range(max_tool_rounds):
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                tools=allowed_tools,
                tool_choice="auto",
                temperature=0
            )

            assistant_message = response.choices[0].message

            # If no tool calls were requested, return the final synthesized answer
            if not assistant_message.tool_calls:
                return assistant_message.content or "The model returned no response."

            # Append assistant's tool call message
            messages.append(assistant_message.model_dump())

            # Execute requested tool calls
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                if tool_name == "get_patient_record" and resolved_pid:
                    arguments["patient_id"] = resolved_pid

                tool_result = self._execute_tool(tool_name, arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

        return "The clinical support agent could not complete the requested analysis within the allowed tool-calling steps."

    def run_offline_loop(self, user_query: str, patient_id: str = None) -> str:
        if self._azure_is_available():
            return self.run_with_azure_openai(user_query=user_query, patient_id=patient_id)

        return "Azure OpenAI configuration is not available."


