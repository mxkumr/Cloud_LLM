"""
Test the improved prompt comparison function with the Hausa example.
"""

import os
import sys
import importlib.util

# Import the pipeline module
pipeline_path = os.path.join(os.path.dirname(__file__), "4. OChanged_code_validation_pipeline.py")
spec = importlib.util.spec_from_file_location("code_validation_pipeline", pipeline_path)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

# Hausa code (irrelevant - about capacity calculation)
hausa_code = """# Python code to simulate the described scenario
def calculate_usage():
    # Initial values
    initial_capacity = 1200
    used_capacity = 1000
    additional_usage = 1000
    remaining_capacity = initial_capacity - used_capacity

    # Check if additional usage exceeds remaining capacity
    if additional_usage <= remaining_capacity:
        total_used = used_capacity + additional_usage
        remaining_after = remaining_capacity - additional_usage
    else:
        total_used = initial_capacity
        remaining_after = 0

    return total_used, remaining_after

# Execute the function
total_used, remaining = calculate_usage()
print(f"Total used: {total_used}, Remaining: {remaining}")"""

# Correct code (actually copies bytes)
correct_code = """def memcpy(dest, src, num_bytes):
    \"\"\"
    Copies a number of bytes from one memory location to another.
    \"\"\"
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest"""

# Prompt
prompt = "Generate Python code for the following: A function copies a number of bytes from one memory location to another. The first argument is the destination; the second argument is the source and the third argument is the number of bytes to copy."

print("="*70)
print("TESTING IMPROVED PROMPT COMPARISON")
print("="*70)

print("\n1. Testing Hausa code (irrelevant - capacity calculation):")
print("-"*70)
result_hausa = pipeline.compare_code_with_prompt(hausa_code, prompt)
print(f"Similar: {result_hausa['similar']}")
print(f"Score: {result_hausa['similarity_score']:.2%}")
print(f"Reasoning: {result_hausa['reasoning']}")
print(f"Matched: {result_hausa['matched_keywords']}")
print(f"Missing: {result_hausa['missing_keywords']}")

print("\n2. Testing Correct code (actually copies bytes):")
print("-"*70)
result_correct = pipeline.compare_code_with_prompt(correct_code, prompt)
print(f"Similar: {result_correct['similar']}")
print(f"Score: {result_correct['similarity_score']:.2%}")
print(f"Reasoning: {result_correct['reasoning']}")
print(f"Matched: {result_correct['matched_keywords']}")
print(f"Missing: {result_correct['missing_keywords']}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"Hausa code correctly identified as irrelevant: {not result_hausa['similar']}")
print(f"Correct code correctly identified as relevant: {result_correct['similar']}")
print(f"Score difference: {result_correct['similarity_score'] - result_hausa['similarity_score']:.2%}")

