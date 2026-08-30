from core.agent.clinical_agent import ClinicalAgent


def main():

    print("==================================================")
    print("   AI Clinical Support Agent — Interactive CLI    ")
    print("==================================================")

    agent = ClinicalAgent()

    sample_patient_id = "P-101"

    sample_query = (
        "Summarize recent history and check diabetes "
        "guideline recommendations for Metformin escalation."
    )

    print(
        f"\n[Physician Request]: "
        f"Patient ID = {sample_patient_id}"
    )

    print(
        f"[Physician Request]: "
        f"Prompt = '{sample_query}'\n"
    )

    result = agent.run_offline_loop(
        user_query=sample_query,
        patient_id=sample_patient_id
    )

    print("\n" + result)

    print(
        "\n=================================================="
    )


if __name__ == "__main__":
    main()