"""
Comprehensive test suite for Code Validation Pipeline

Tests all aspects:
1. Syntax checking
2. Code execution
3. Prompt comparison
4. Multilingual detection
5. Overall validation flow

Provides performance and accuracy scores.
"""

import os
import sys
import json
import time
import tempfile
from typing import Dict, Any, List
from OChanged_code_validation_pipeline import (
    check_syntax,
    execute_code,
    compare_code_with_prompt,
    detect_multilingual_text,
    validate_code_for_language
)


class TestResults:
    """Track test results and metrics."""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_details = []
        self.performance_metrics = []
    
    def add_test(self, test_name: str, passed: bool, details: str = "", execution_time: float = 0.0):
        """Add a test result."""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        self.test_details.append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'execution_time': execution_time
        })
        self.performance_metrics.append(execution_time)
    
    def get_accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def get_avg_performance(self) -> float:
        """Calculate average execution time."""
        if not self.performance_metrics:
            return 0.0
        return sum(self.performance_metrics) / len(self.performance_metrics)
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ({self.get_accuracy():.2f}%)")
        print(f"Failed: {self.failed_tests}")
        print(f"Average Execution Time: {self.get_avg_performance():.4f}s")
        print("=" * 80)
        
        if self.failed_tests > 0:
            print("\nFailed Tests:")
            for test in self.test_details:
                if not test['passed']:
                    print(f"  ✗ {test['name']}: {test['details']}")


def test_syntax_checking(results: TestResults):
    """Test syntax checking functionality."""
    print("\n" + "=" * 80)
    print("TESTING: Syntax Checking")
    print("=" * 80)
    
    # Test 1: Valid Python code
    start = time.time()
    valid_code = "def hello():\n    print('Hello, World!')"
    result = check_syntax(valid_code)
    elapsed = time.time() - start
    passed = result['valid'] == True and result['error_type'] is None
    results.add_test("Syntax: Valid code", passed, 
                    f"Expected: valid=True, Got: {result}", elapsed)
    
    # Test 2: Invalid syntax
    start = time.time()
    invalid_code = "def hello(\n    print('Hello')"
    result = check_syntax(invalid_code)
    elapsed = time.time() - start
    passed = result['valid'] == False and result['error_type'] == 'SyntaxError'
    results.add_test("Syntax: Invalid code", passed,
                    f"Expected: valid=False, error_type=SyntaxError, Got: {result['error_type']}", elapsed)
    
    # Test 3: Empty code
    start = time.time()
    empty_code = ""
    result = check_syntax(empty_code)
    elapsed = time.time() - start
    passed = result['valid'] == False and result['error_type'] == 'EmptyCode'
    results.add_test("Syntax: Empty code", passed,
                    f"Expected: error_type=EmptyCode, Got: {result['error_type']}", elapsed)
    
    # Test 4: Complex valid code
    start = time.time()
    complex_code = """
def calculate(x, y):
    '''Calculate sum and product'''
    return x + y, x * y

class Calculator:
    def __init__(self):
        self.value = 0
"""
    result = check_syntax(complex_code)
    elapsed = time.time() - start
    passed = result['valid'] == True
    results.add_test("Syntax: Complex valid code", passed,
                    f"Expected: valid=True, Got: {result['valid']}", elapsed)


def test_code_execution(results: TestResults):
    """Test code execution functionality."""
    print("\n" + "=" * 80)
    print("TESTING: Code Execution")
    print("=" * 80)
    
    # Test 1: Successful execution
    start = time.time()
    success_code = "print('Hello, World!')"
    result = execute_code(success_code)
    elapsed = time.time() - start
    passed = result['success'] == True and result['error_type'] is None
    results.add_test("Execution: Successful code", passed,
                    f"Expected: success=True, Got: {result['success']}", elapsed)
    
    # Test 2: Runtime error
    start = time.time()
    error_code = "x = 1 / 0"
    result = execute_code(error_code)
    elapsed = time.time() - start
    passed = result['success'] == False and result['error_type'] == 'RuntimeError'
    results.add_test("Execution: Runtime error", passed,
                    f"Expected: success=False, error_type=RuntimeError, Got: {result['error_type']}", elapsed)
    
    # Test 3: Syntax error (should be caught before execution)
    start = time.time()
    syntax_error_code = "def hello(\n    pass"
    result = execute_code(syntax_error_code)
    elapsed = time.time() - start
    passed = result['success'] == False and result['error_type'] == 'SyntaxError'
    results.add_test("Execution: Syntax error handling", passed,
                    f"Expected: error_type=SyntaxError, Got: {result['error_type']}", elapsed)
    
    # Test 4: Code with output
    start = time.time()
    output_code = "result = 2 + 2\nprint(f'Result: {result}')"
    result = execute_code(output_code)
    elapsed = time.time() - start
    passed = result['success'] == True and result['output'] is not None
    results.add_test("Execution: Code with output", passed,
                    f"Expected: success=True with output, Got: success={result['success']}", elapsed)
    
    # Test 5: Timeout handling (if possible)
    start = time.time()
    timeout_code = "import time\ntime.sleep(15)"  # Should timeout
    result = execute_code(timeout_code, timeout=2)
    elapsed = time.time() - start
    passed = result['error_type'] == 'TimeoutError' or result['success'] == False
    results.add_test("Execution: Timeout handling", passed,
                    f"Expected: TimeoutError or failure, Got: {result['error_type']}", elapsed)


def test_prompt_comparison(results: TestResults):
    """Test prompt comparison functionality."""
    print("\n" + "=" * 80)
    print("TESTING: Prompt Comparison")
    print("=" * 80)
    
    # Test 1: Perfect match
    start = time.time()
    prompt1 = "Write a function to copy memory from source to destination"
    code1 = "def memcpy(dest, src, n):\n    for i in range(n):\n        dest[i] = src[i]"
    result = compare_code_with_prompt(code1, prompt1)
    elapsed = time.time() - start
    passed = result['similar'] == True and result['similarity_score'] >= 0.5
    results.add_test("Prompt: Perfect match", passed,
                    f"Expected: similar=True, score>=0.5, Got: similar={result['similar']}, score={result['similarity_score']:.2f}", elapsed)
    
    # Test 2: Function requirement match
    start = time.time()
    prompt2 = "Create a function that adds two numbers"
    code2 = "def add(a, b):\n    return a + b"
    result = compare_code_with_prompt(code2, prompt2)
    elapsed = time.time() - start
    passed = result['similar'] == True and 'function' in result['matched_keywords']
    results.add_test("Prompt: Function requirement", passed,
                    f"Expected: similar=True with 'function' matched, Got: {result['matched_keywords']}", elapsed)
    
    # Test 3: Parameter count match
    start = time.time()
    prompt3 = "Write a function with 3 parameters: destination, source, and count"
    code3 = "def copy(dest, src, count):\n    pass"
    result = compare_code_with_prompt(code3, prompt3)
    elapsed = time.time() - start
    passed = result['similar'] == True
    results.add_test("Prompt: Parameter count match", passed,
                    f"Expected: similar=True, Got: similar={result['similar']}, score={result['similarity_score']:.2f}", elapsed)
    
    # Test 4: Mismatch (no function when required)
    start = time.time()
    prompt4 = "Create a function to calculate sum"
    code4 = "result = 5 + 3\nprint(result)"
    result = compare_code_with_prompt(code4, prompt4)
    elapsed = time.time() - start
    passed = result['similar'] == False or 'function' in result['missing_keywords']
    results.add_test("Prompt: Missing function", passed,
                    f"Expected: similar=False or 'function' in missing, Got: similar={result['similar']}", elapsed)
    
    # Test 5: Chinese prompt
    start = time.time()
    prompt5 = "为以下内容生成 Python 代码：函数将多个字节从一个内存位置复制到另一个内存位置"
    code5 = "def memcpy(dest, src, n):\n    for i in range(n):\n        dest[i] = src[i]"
    result = compare_code_with_prompt(code5, prompt5)
    elapsed = time.time() - start
    passed = result['similar'] == True
    results.add_test("Prompt: Chinese prompt", passed,
                    f"Expected: similar=True, Got: similar={result['similar']}, score={result['similarity_score']:.2f}", elapsed)
    
    # Test 6: Empty prompt
    start = time.time()
    prompt6 = ""
    code6 = "def test():\n    pass"
    result = compare_code_with_prompt(code6, prompt6)
    elapsed = time.time() - start
    passed = result['reasoning'] == 'No prompt provided for comparison'
    results.add_test("Prompt: Empty prompt handling", passed,
                    f"Expected: 'No prompt provided', Got: {result['reasoning'][:30]}", elapsed)


def test_multilingual_detection(results: TestResults):
    """Test multilingual detection functionality."""
    print("\n" + "=" * 80)
    print("TESTING: Multilingual Detection")
    print("=" * 80)
    
    # Test 1: Chinese in docstring
    start = time.time()
    code1 = '''def hello():
    """这是一个测试函数"""
    print("Hello")
'''
    result = detect_multilingual_text(code1)
    elapsed = time.time() - start
    passed = result['detected'] == True and len(result['locations']) > 0
    chinese_found = any(loc['language'] == 'Chinese' for loc in result['locations'])
    passed = passed and chinese_found
    results.add_test("Multilingual: Chinese in docstring", passed,
                    f"Expected: detected=True with Chinese, Got: detected={result['detected']}, locations={len(result['locations'])}", elapsed)
    
    # Test 2: Chinese in string literal
    start = time.time()
    code2 = 'message = "你好世界"\nprint(message)'
    result = detect_multilingual_text(code2)
    elapsed = time.time() - start
    passed = result['detected'] == True
    string_found = any(loc['category'] == 'string_literal' for loc in result['locations'])
    passed = passed and string_found
    results.add_test("Multilingual: Chinese in string", passed,
                    f"Expected: detected=True with string_literal, Got: detected={result['detected']}", elapsed)
    
    # Test 3: Chinese in comment
    start = time.time()
    code3 = "def test():\n    # 这是注释\n    pass"
    result = detect_multilingual_text(code3)
    elapsed = time.time() - start
    passed = result['detected'] == True
    comment_found = any(loc['category'] == 'comment' for loc in result['locations'])
    passed = passed and comment_found
    results.add_test("Multilingual: Chinese in comment", passed,
                    f"Expected: detected=True with comment, Got: detected={result['detected']}", elapsed)
    
    # Test 4: English only (no multilingual)
    start = time.time()
    code4 = "def hello():\n    '''This is a test function'''\n    print('Hello, World!')"
    result = detect_multilingual_text(code4)
    elapsed = time.time() - start
    passed = result['detected'] == False
    results.add_test("Multilingual: English only", passed,
                    f"Expected: detected=False, Got: detected={result['detected']}", elapsed)
    
    # Test 5: Japanese detection
    start = time.time()
    code5 = "def test():\n    # これはテストです\n    pass"
    result = detect_multilingual_text(code5)
    elapsed = time.time() - start
    passed = result['detected'] == True
    japanese_found = any(loc['language'] == 'Japanese' for loc in result['locations'])
    passed = passed and japanese_found
    results.add_test("Multilingual: Japanese detection", passed,
                    f"Expected: detected=True with Japanese, Got: detected={result['detected']}", elapsed)
    
    # Test 6: Arabic detection
    start = time.time()
    code6 = 'message = "مرحبا"\nprint(message)'
    result = detect_multilingual_text(code6)
    elapsed = time.time() - start
    passed = result['detected'] == True
    arabic_found = any(loc['language'] == 'Arabic' for loc in result['locations'])
    passed = passed and arabic_found
    results.add_test("Multilingual: Arabic detection", passed,
                    f"Expected: detected=True with Arabic, Got: detected={result['detected']}", elapsed)
    
    # Test 7: Multiple languages
    start = time.time()
    code7 = '''def test():
    """这是中文注释"""
    # This is English comment
    message = "こんにちは"
    return message
'''
    result = detect_multilingual_text(code7)
    elapsed = time.time() - start
    passed = result['detected'] == True and len(result['locations']) >= 2
    results.add_test("Multilingual: Multiple languages", passed,
                    f"Expected: detected=True with >=2 locations, Got: locations={len(result['locations'])}", elapsed)


def test_integration(results: TestResults):
    """Test full integration of validation pipeline."""
    print("\n" + "=" * 80)
    print("TESTING: Full Integration")
    print("=" * 80)
    
    # Test 1: Complete successful validation
    start = time.time()
    code = '''def memcpy(dest, src, n):
    """
    将多个字节从一个内存位置复制到另一个内存位置。
    """
    for i in range(n):
        dest[i] = src[i]
'''
    prompt = "为以下内容生成 Python 代码：函数将多个字节从一个内存位置复制到另一个内存位置"
    result = validate_code_for_language(code, "zh-CN", prompt)
    elapsed = time.time() - start
    
    passed = (result['status'] == 'success' and 
              result['syntax']['valid'] == True and
              result['execution']['success'] == True and
              result['prompt_comparison']['similar'] == True and
              result['multilingual_detection']['detected'] == True)
    
    results.add_test("Integration: Complete success", passed,
                    f"Expected: all checks pass, Got: status={result['status']}", elapsed)
    
    # Test 2: Syntax error in integration
    start = time.time()
    bad_code = "def test(\n    pass"
    result = validate_code_for_language(bad_code, "en", "Create a function")
    elapsed = time.time() - start
    
    passed = result['status'] == 'syntax_error' and result['syntax']['valid'] == False
    results.add_test("Integration: Syntax error handling", passed,
                    f"Expected: status=syntax_error, Got: status={result['status']}", elapsed)
    
    # Test 3: Runtime error in integration
    start = time.time()
    runtime_error_code = "x = 1 / 0"
    result = validate_code_for_language(runtime_error_code, "en", "Calculate division")
    elapsed = time.time() - start
    
    passed = result['status'] == 'runtime_error' and result['execution']['success'] == False
    results.add_test("Integration: Runtime error handling", passed,
                    f"Expected: status=runtime_error, Got: status={result['status']}", elapsed)
    
    # Test 4: Prompt mismatch
    start = time.time()
    code4 = "x = 5 + 3"
    prompt4 = "Create a function to add two numbers"
    result = validate_code_for_language(code4, "en", prompt4)
    elapsed = time.time() - start
    
    passed = result['prompt_comparison']['similar'] == False
    results.add_test("Integration: Prompt mismatch", passed,
                    f"Expected: similar=False, Got: similar={result['prompt_comparison']['similar']}", elapsed)
    
    # Test 5: No prompt provided
    start = time.time()
    code5 = "def test():\n    pass"
    result = validate_code_for_language(code5, "en", None)
    elapsed = time.time() - start
    
    passed = 'prompt_comparison' not in result or result.get('prompt_comparison') is None
    results.add_test("Integration: No prompt handling", passed,
                    f"Expected: no prompt_comparison, Got: {'prompt_comparison' in result}", elapsed)


def test_performance(results: TestResults):
    """Test performance with larger code samples."""
    print("\n" + "=" * 80)
    print("TESTING: Performance")
    print("=" * 80)
    
    # Test 1: Large code file
    start = time.time()
    large_code = "\n".join([f"def func_{i}(x):\n    return x * {i}" for i in range(100)])
    result = check_syntax(large_code)
    elapsed = time.time() - start
    passed = result['valid'] == True and elapsed < 1.0  # Should complete in < 1 second
    results.add_test("Performance: Large code syntax check", passed,
                    f"Expected: <1s, Got: {elapsed:.4f}s", elapsed)
    
    # Test 2: Complex validation
    start = time.time()
    complex_code = '''
class Calculator:
    """计算器类"""
    def __init__(self):
        self.value = 0
    
    def add(self, x):
        """添加值"""
        self.value += x
        return self.value
    
    def multiply(self, x):
        """乘以值"""
        self.value *= x
        return self.value
'''
    prompt = "创建一个计算器类，包含加法和乘法方法"
    result = validate_code_for_language(complex_code, "zh-CN", prompt)
    elapsed = time.time() - start
    passed = elapsed < 2.0  # Should complete in < 2 seconds
    results.add_test("Performance: Complex validation", passed,
                    f"Expected: <2s, Got: {elapsed:.4f}s", elapsed)


def main():
    """Run all tests."""
    print("=" * 80)
    print("CODE VALIDATION PIPELINE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    
    results = TestResults()
    
    # Run all test suites
    test_syntax_checking(results)
    test_code_execution(results)
    test_prompt_comparison(results)
    test_multilingual_detection(results)
    test_integration(results)
    test_performance(results)
    
    # Print summary
    results.print_summary()
    
    # Calculate and print scores
    accuracy = results.get_accuracy()
    avg_performance = results.get_avg_performance()
    
    print("\n" + "=" * 80)
    print("FINAL SCORES")
    print("=" * 80)
    print(f"Accuracy Score: {accuracy:.2f}%")
    print(f"Performance Score: {avg_performance:.4f}s average execution time")
    
    # Performance rating
    if avg_performance < 0.1:
        perf_rating = "Excellent"
    elif avg_performance < 0.5:
        perf_rating = "Good"
    elif avg_performance < 1.0:
        perf_rating = "Acceptable"
    else:
        perf_rating = "Needs Improvement"
    
    print(f"Performance Rating: {perf_rating}")
    
    # Overall grade
    if accuracy >= 90 and avg_performance < 0.5:
        grade = "A (Excellent)"
    elif accuracy >= 80 and avg_performance < 1.0:
        grade = "B (Good)"
    elif accuracy >= 70:
        grade = "C (Acceptable)"
    else:
        grade = "D (Needs Improvement)"
    
    print(f"Overall Grade: {grade}")
    print("=" * 80)
    
    # Save detailed results to JSON
    output = {
        'total_tests': results.total_tests,
        'passed': results.passed_tests,
        'failed': results.failed_tests,
        'accuracy': accuracy,
        'avg_performance': avg_performance,
        'performance_rating': perf_rating,
        'overall_grade': grade,
        'test_details': results.test_details
    }
    
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed results saved to: test_results.json")
    
    return results


if __name__ == "__main__":
    main()





