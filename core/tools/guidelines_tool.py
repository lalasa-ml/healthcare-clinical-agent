import json
import re
from pathlib import Path
from typing import Any


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

# Resolve the project root based on this Python file.
#
# Expected structure:
#
# healthcare-clinical-agent/
# ├── app/
# ├── core/
# │   └── tools/
# │       └── guidelines_tool.py
# └── data/
#     └── guidelines/
#         └── diabetes_protocol.txt
#
PROJECT_ROOT = Path(__file__).resolve().parents[2]


GUIDELINES_FILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "guidelines"
    / "diabetes_protocol.txt"
)


# ---------------------------------------------------------
# Common words that do not provide useful search information
# ---------------------------------------------------------

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "check",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "patient",
    "recent",
    "recommendation",
    "recommendations",
    "summarize",
    "summary",
    "the",
    "to",
    "what",
    "with",
}


# ---------------------------------------------------------
# Helper: extract meaningful search terms
# ---------------------------------------------------------

def _extract_search_terms(topic: str) -> list[str]:
    """
    Extract meaningful words from a clinical guideline query.

    Example:

        "diabetes medication management Metformin escalation"

    may become:

        [
            "diabetes",
            "medication",
            "management",
            "metformin",
            "escalation"
        ]
    """

    if not isinstance(topic, str):
        return []

    words = re.findall(
        r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)*",
        topic.lower()
    )

    search_terms = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    ]

    return search_terms


# ---------------------------------------------------------
# Helper: load guideline document
# ---------------------------------------------------------

def _load_guideline_document() -> str:
    """
    Loads the internal clinical guideline document.

    Returns:
        The complete guideline document as text.

    Raises:
        FileNotFoundError:
            If the guideline file does not exist.

        OSError:
            If the file cannot be accessed.
    """

    if not GUIDELINES_FILE_PATH.exists():
        raise FileNotFoundError(
            "Clinical guideline document was not found at: "
            f"{GUIDELINES_FILE_PATH}"
        )

    with open(
        GUIDELINES_FILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()


# ---------------------------------------------------------
# Main guideline retrieval tool
# ---------------------------------------------------------

def search_guidelines(topic: str) -> str:
    """
    Searches the internal clinical guideline document.

    This function is designed to be exposed as an agent tool.

    Args:
        topic:
            The clinical topic or question to search for.

    Returns:
        A JSON string containing:

        - success status
        - search topic
        - search terms
        - number of matching sections
        - matching guideline sections
        - source document
    """

    # -----------------------------------------------------
    # STEP 1: Validate input
    # -----------------------------------------------------

    if topic is None:
        return json.dumps(
            {
                "success": False,
                "error": "Guideline search topic is required."
            },
            indent=2
        )

    if not isinstance(topic, str):
        return json.dumps(
            {
                "success": False,
                "error": "Guideline search topic must be a string."
            },
            indent=2
        )

    topic = topic.strip()

    if not topic:
        return json.dumps(
            {
                "success": False,
                "error": "Guideline search topic cannot be empty."
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 2: Extract meaningful search terms
    # -----------------------------------------------------

    search_terms = _extract_search_terms(topic)

    if not search_terms:
        return json.dumps(
            {
                "success": False,
                "error": (
                    "No meaningful clinical search terms "
                    "could be extracted from the topic."
                ),
                "topic": topic
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 3: Load guideline document
    # -----------------------------------------------------

    try:

        content = _load_guideline_document()

    except FileNotFoundError as exc:

        return json.dumps(
            {
                "success": False,
                "error": str(exc),
                "topic": topic
            },
            indent=2
        )

    except OSError as exc:

        return json.dumps(
            {
                "success": False,
                "error": (
                    "Unable to access clinical guideline "
                    f"document: {str(exc)}"
                ),
                "topic": topic
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 4: Split guideline into sections
    # -----------------------------------------------------

    sections = [
        section.strip()
        for section in content.split("\n\n")
        if section.strip()
    ]

    # -----------------------------------------------------
    # STEP 5: Score each section
    # -----------------------------------------------------

    scored_sections: list[dict[str, Any]] = []

    for section in sections:

        section_lower = section.lower()

        matched_terms = [
            term
            for term in search_terms
            if term in section_lower
        ]

        if matched_terms:

            score = len(matched_terms)

            scored_sections.append(
                {
                    "score": score,
                    "matched_terms": matched_terms,
                    "section": section
                }
            )

    # -----------------------------------------------------
    # STEP 6: Sort sections by relevance
    # -----------------------------------------------------

    scored_sections.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # -----------------------------------------------------
    # STEP 7: Handle no matching evidence
    # -----------------------------------------------------

    if not scored_sections:

        return json.dumps(
            {
                "success": True,
                "topic": topic,
                "search_terms": search_terms,
                "source": "data/guidelines/diabetes_protocol.txt",
                "matching_sections": [],
                "match_count": 0,
                "message": (
                    "No relevant clinical guideline evidence "
                    "was found in the internal guideline document "
                    "for the supplied search topic."
                )
            },
            indent=2
        )

    # -----------------------------------------------------
    # STEP 8: Prepare results
    # -----------------------------------------------------

    matching_sections = []

    for item in scored_sections:

        matching_sections.append(
            {
                "relevance_score": item["score"],
                "matched_terms": item["matched_terms"],
                "content": item["section"]
            }
        )

    # -----------------------------------------------------
    # STEP 9: Return structured result
    # -----------------------------------------------------

    result = {
        "success": True,
        "topic": topic,
        "search_terms": search_terms,
        "source": "data/guidelines/diabetes_protocol.txt",
        "match_count": len(matching_sections),
        "matching_sections": matching_sections
    }

    return json.dumps(
        result,
        indent=2
    )


# ---------------------------------------------------------
# Backward-compatible function name
# ---------------------------------------------------------

def search_clinical_guidelines(query: str) -> str:
    """
    Backward-compatible wrapper.

    Existing code that calls:

        search_clinical_guidelines(query)

    will continue to work.

    New code should use:

        search_guidelines(topic)
    """

    return search_guidelines(query)