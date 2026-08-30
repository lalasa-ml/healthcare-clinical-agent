import json
from core.agent.clinical_agent import ClinicalAgent

def run_evaluation():
    print("==================================================")
    print("      Agentic AI Evaluation Suite Execution      ")
    print("==================================================")
    
    with open("tests/eval_dataset.json", "r") as f:
        eval_cases = json.load(f)
        
    agent = ClinicalAgent()
    passed = 0
    
    for case in eval_cases:
        print(f"\nRunning Eval Case [{case['eval_id']}]...")
        output = agent.run_offline_loop(user_query=case['prompt'], patient_id=case['patient_id'])
        
        # Verify grounding keywords
        grounded = all(kw in output for kw in case['expected_grounding_keywords'])
        if grounded:
            print(f"✅ [{case['eval_id']}] PASSED: Output properly grounded in patient/guideline data.")
            passed += 1
        else:
            print(f"❌ [{case['eval_id']}] FAILED: Missing key grounded terms.")
            
    print("\n==================================================")
    print(f" Evaluation Summary: {passed}/{len(eval_cases)} Passed")
    print("==================================================")

if __name__ == "__main__":
    run_evaluation()