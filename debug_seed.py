from src.ui import extract_workflow_inputs

workflow_zero = {"1": {"inputs": {"seed": 0}}}
workflow_nonzero = {"1": {"inputs": {"seed": 5}}}

extracted_zero = extract_workflow_inputs(workflow_zero)
seed_input_zero = extracted_zero[0]["inputs"][0]
print(f"Seed 0 Randomize: {seed_input_zero['randomize']}")

extracted_nonzero = extract_workflow_inputs(workflow_nonzero)
seed_input_nonzero = extracted_nonzero[0]["inputs"][0]
print(f"Seed 5 Randomize: {seed_input_nonzero['randomize']}")
