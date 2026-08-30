import pytest
from core.agent.clinical_agent import ClinicalAgent

@pytest.fixture
def agent():
    return ClinicalAgent()

# ---------------------------------------------------------
# Tool Selection Tests Across All 4 Categories
# ---------------------------------------------------------

def test_category_a_patient_fact_query(agent):
    """Category A: Should ONLY select get_patient_record"""
    query = "What medications is P-101 taking?"
    allowed_tools = agent._select_allowed_tools(user_query=query, patient_id="P-101")
    tool_names = [t["function"]["name"] for t in allowed_tools]
    
    assert "get_patient_record" in tool_names
    assert "search_guidelines" not in tool_names


def test_category_b_general_guideline_query(agent):
    """Category B: Should ONLY select search_guidelines even if patient_id is passed"""
    query = "What does the hospital guideline recommend for metformin escalation in type 2 diabetes?"
    allowed_tools = agent._select_allowed_tools(user_query=query, patient_id="P-101")
    tool_names = [t["function"]["name"] for t in allowed_tools]
    
    assert "search_guidelines" in tool_names
    assert "get_patient_record" not in tool_names


def test_category_c_patient_guideline_query(agent):
    """Category C: Should select BOTH get_patient_record and search_guidelines"""
    query = "For patient P-101, what does the hospital guideline say about her HbA1c of 8.2%?"
    allowed_tools = agent._select_allowed_tools(user_query=query, patient_id="P-101")
    tool_names = [t["function"]["name"] for t in allowed_tools]
    
    assert "get_patient_record" in tool_names
    assert "search_guidelines" in tool_names


def test_category_d_treatment_decision_query(agent):
    """Category D: Should select BOTH tools for prescribing questions"""
    query = "Should I prescribe a GLP-1 receptor agonist to patient P-101 today?"
    allowed_tools = agent._select_allowed_tools(user_query=query, patient_id="P-101")
    tool_names = [t["function"]["name"] for t in allowed_tools]
    
    assert "get_patient_record" in tool_names
    assert "search_guidelines" in tool_names