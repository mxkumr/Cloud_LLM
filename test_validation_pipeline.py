"""
Comprehensive Test Suite for Code Validation Pipeline

Tests accuracy, performance, and reliability of the code validation pipeline
with focus on multilingual text detection.

Usage:
    python test_validation_pipeline.py
"""

import os
import sys
import json
import time
import importlib.util
from typing import Dict, Any, List

# Import the pipeline module (handling the filename with spaces and numbers)
pipeline_path = os.path.join(os.path.dirname(__file__), "4. OChanged_code_validation_pipeline.py")
spec = importlib.util.spec_from_file_location("code_validation_pipeline", pipeline_path)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)

# Import functions from the pipeline
check_syntax = pipeline.check_syntax
execute_code = pipeline.execute_code
compare_code_with_prompt = pipeline.compare_code_with_prompt
detect_multilingual_text = pipeline.detect_multilingual_text
validate_code_for_language = pipeline.validate_code_for_language
generate_validation_summary_table = pipeline.generate_validation_summary_table


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
        
        if execution_time > 0:
            self.performance_metrics.append({
                'test': test_name,
                'time': execution_time
            })
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)")
        print(f"Failed: {self.failed_tests} ({self.failed_tests/self.total_tests*100:.1f}%)")
        
        if self.performance_metrics:
            avg_time = sum(m['time'] for m in self.performance_metrics) / len(self.performance_metrics)
            max_time = max(m['time'] for m in self.performance_metrics)
            print(f"\nPerformance Metrics:")
            print(f"  Average execution time: {avg_time*1000:.2f}ms")
            print(f"  Maximum execution time: {max_time*1000:.2f}ms")
        
        print("\nFailed Tests:")
        for test in self.test_details:
            if not test['passed']:
                print(f"  ✗ {test['name']}: {test['details']}")
        
        print("="*70)


# Global test results tracker
test_results = TestResults()


def test_multilingual_detection():
    """Test multilingual text detection with various languages."""
    print("\n" + "="*70)
    print("TESTING MULTILINGUAL DETECTION")
    print("="*70)
    
    # Test Case 1: Chinese docstring
    test_code_1 = '''"""
将多个字节从一个内存位置复制到另一个内存位置。

参数:
    dest: 目标内存位置（可写入的字节序列，如 bytearray）
    src: 源内存位置（可读取的字节序列，如 bytes 或 bytearray）
    num_bytes: 要复制的字节数
"""
def memcpy(dest, src, num_bytes):
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_1)
    elapsed = time.time() - start
    
    passed = result['detected'] and len(result['locations']) > 0
    chinese_found = any(
        'Chinese' in loc.get('language', '') or 'Mandarin' in loc.get('language', '')
        for loc in result['locations']
    )
    passed = passed and chinese_found
    test_results.add_test(
        "Chinese docstring detection",
        passed,
        f"Detected: {result['detected']}, Locations: {len(result['locations'])}, Chinese found: {chinese_found}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Chinese docstring detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 2: Hindi comments
    test_code_2 = '''def copy_bytes(dest, src, num_bytes):
    # सुनिश्चित करें कि destination एक bytearray है ताकि उसे बदला जा सके
    # सुनिश्चित करें कि source एक bytearray है
    # कॉपी करने की सीमा को सीमित करें
    # बाइट्स कॉपी करें
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_2)
    elapsed = time.time() - start
    
    passed = result['detected']
    hindi_comments = [loc for loc in result['locations'] 
                     if loc.get('language') == 'Hindi' and loc.get('category') == 'comment']
    passed = passed and len(hindi_comments) > 0
    test_results.add_test(
        "Hindi comments detection",
        passed,
        f"Detected: {result['detected']}, Hindi comments: {len(hindi_comments)}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Hindi comments detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 3: Spanish string literals
    test_code_3 = '''def memcpy(dest, src, num_bytes):
    error_msg = "Error: No se pudo copiar los bytes de la ubicación de memoria"
    success_msg = "Éxito: Bytes copiados correctamente"
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_3)
    elapsed = time.time() - start
    
    passed = result['detected']
    spanish_strings = [loc for loc in result['locations']
                      if loc.get('language') == 'Spanish' and loc.get('category') == 'string_literal']
    passed = passed and len(spanish_strings) > 0
    test_results.add_test(
        "Spanish string literals detection",
        passed,
        f"Detected: {result['detected']}, Spanish strings: {len(spanish_strings)}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Spanish string literals detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 4: French docstring and comments
    test_code_4 = '''"""
Copie un certain nombre d'octets d'un emplacement mémoire à un autre.

Args:
    dest: Liste d'octets de destination
    src: Liste d'octets source
    num_bytes: Nombre d'octets à copier
"""
def memcpy(dest, src, num_bytes):
    # Si la source ou la destination est trop petite, on arrête
    if len(src) < num_bytes or len(dest) < num_bytes:
        return None
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_4)
    elapsed = time.time() - start
    
    passed = result['detected']
    french_locations = [loc for loc in result['locations'] if loc.get('language') == 'French']
    passed = passed and len(french_locations) > 0
    test_results.add_test(
        "French docstring and comments",
        passed,
        f"Detected: {result['detected']}, French locations: {len(french_locations)}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} French docstring and comments ({elapsed*1000:.2f}ms)")
    
    # Test Case 5: Mixed languages
    test_code_5 = '''"""
将多个字节从一个内存位置复制到另一个内存位置。
Copia una cantidad de bytes de una ubicación de memoria a otra.
Copie un certain nombre d'octets d'un emplacement mémoire à un autre.
"""
def memcpy(dest, src, num_bytes):
    # सुनिश्चित करें कि destination एक bytearray है
    # Asegurarse de que num_bytes no exceda el tamaño de la fuente
    # Si la source est trop petite, on arrête
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_5)
    elapsed = time.time() - start
    
    passed = result['detected']
    languages = set(loc.get('language') for loc in result['locations'])
    passed = passed and len(languages) > 1
    test_results.add_test(
        "Mixed languages detection",
        passed,
        f"Detected: {result['detected']}, Languages found: {len(languages)} ({', '.join(list(languages)[:3])})",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Mixed languages detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 6: Japanese code
    test_code_6 = '''def memcpy(dest, src, num_bytes):
    """
    あるメモリ位置から別のメモリ位置に多数のバイトをコピーします。
    
    Args:
        dest: 宛先のメモリ位置（リストやバイト列など）
        src: ソースのメモリ位置（リストやバイト列など）
        num_bytes: コピーするバイト数
    """
    # リストの場合はスライスでコピー
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_6)
    elapsed = time.time() - start
    
    passed = result['detected']
    japanese_found = any('Japanese' in loc.get('language', '') for loc in result['locations'])
    passed = passed and japanese_found
    test_results.add_test(
        "Japanese code detection",
        passed,
        f"Detected: {result['detected']}, Japanese found: {japanese_found}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Japanese code detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 7: Russian docstring
    test_code_7 = '''"""
Копирует определенное количество байтов из одного места памяти в другое.

Аргументы:
    destination: место назначения (байтовый массив)
    source: источник (байтовый массив)
    num_bytes: количество байтов для копирования
"""
def memcpy(dest, src, num_bytes):
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_7)
    elapsed = time.time() - start
    
    passed = result['detected']
    russian_found = any(loc.get('language') == 'Russian' for loc in result['locations'])
    passed = passed and russian_found
    test_results.add_test(
        "Russian docstring detection",
        passed,
        f"Detected: {result['detected']}, Russian found: {russian_found}",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Russian docstring detection ({elapsed*1000:.2f}ms)")
    
    # Test Case 8: Pure English (should not be detected)
    test_code_8 = '''"""
Copy a number of bytes from one memory location to another.

Args:
    dest: Destination memory location
    src: Source memory location
    num_bytes: Number of bytes to copy
"""
def memcpy(dest, src, num_bytes):
    # Ensure destination is large enough
    if len(dest) < num_bytes:
        return None
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = detect_multilingual_text(test_code_8)
    elapsed = time.time() - start
    
    passed = not result['detected']  # Should NOT detect English as multilingual
    test_results.add_test(
        "Pure English code (no detection)",
        passed,
        f"Detected: {result['detected']}, Expected: False",
        elapsed
    )
    print(f"{'✓' if passed else '✗'} Pure English code (no detection) ({elapsed*1000:.2f}ms)")


def test_syntax_validation():
    """Test syntax validation."""
    print("\n" + "="*70)
    print("TESTING SYNTAX VALIDATION")
    print("="*70)
    
    # Valid code
    code = "def test(): return 42"
    start = time.time()
    result = check_syntax(code)
    elapsed = time.time() - start
    passed = result['valid'] and result['error_type'] is None
    test_results.add_test("Valid syntax", passed, f"Valid: {result['valid']}", elapsed)
    print(f"{'✓' if passed else '✗'} Valid syntax ({elapsed*1000:.2f}ms)")
    
    # Syntax error
    code = "def test( return 42"
    start = time.time()
    result = check_syntax(code)
    elapsed = time.time() - start
    passed = not result['valid'] and result['error_type'] == 'SyntaxError'
    test_results.add_test("Syntax error detection", passed, f"Error type: {result['error_type']}", elapsed)
    print(f"{'✓' if passed else '✗'} Syntax error detection ({elapsed*1000:.2f}ms)")
    
    # Empty code
    code = ""
    start = time.time()
    result = check_syntax(code)
    elapsed = time.time() - start
    passed = not result['valid'] and result['error_type'] == 'EmptyCode'
    test_results.add_test("Empty code handling", passed, f"Error type: {result['error_type']}", elapsed)
    print(f"{'✓' if passed else '✗'} Empty code handling ({elapsed*1000:.2f}ms)")


def test_code_execution():
    """Test code execution."""
    print("\n" + "="*70)
    print("TESTING CODE EXECUTION")
    print("="*70)
    
    # Successful execution
    code = "result = 2 + 2\nprint(result)"
    start = time.time()
    result = execute_code(code)
    elapsed = time.time() - start
    passed = result['success'] and result['error_type'] is None
    test_results.add_test("Successful execution", passed, f"Success: {result['success']}", elapsed)
    print(f"{'✓' if passed else '✗'} Successful execution ({elapsed*1000:.2f}ms)")
    
    # Runtime error
    code = "x = 1 / 0"
    start = time.time()
    result = execute_code(code)
    elapsed = time.time() - start
    passed = not result['success'] and result['error_type'] == 'RuntimeError'
    test_results.add_test("Runtime error handling", passed, f"Error type: {result['error_type']}", elapsed)
    print(f"{'✓' if passed else '✗'} Runtime error handling ({elapsed*1000:.2f}ms)")
    
    # Code with multilingual output
    code = '''# 测试多语言输出
msg = "测试成功"
print(msg)
'''
    start = time.time()
    result = execute_code(code)
    elapsed = time.time() - start
    passed = result['success']
    test_results.add_test("Code with multilingual output", passed, f"Success: {result['success']}", elapsed)
    print(f"{'✓' if passed else '✗'} Code with multilingual output ({elapsed*1000:.2f}ms)")


def test_prompt_comparison():
    """Test prompt comparison."""
    print("\n" + "="*70)
    print("TESTING PROMPT COMPARISON")
    print("="*70)
    
    # Exact match
    prompt = "Write a function that copies bytes from one memory location to another"
    code = '''def memcpy(dest, src, num_bytes):
    """Copy bytes from source to destination."""
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    start = time.time()
    result = compare_code_with_prompt(code, prompt)
    elapsed = time.time() - start
    passed = result['similar'] and result['similarity_score'] > 0.5
    test_results.add_test("Exact prompt match", passed, 
                         f"Similar: {result['similar']}, Score: {result['similarity_score']:.2f}", elapsed)
    print(f"{'✓' if passed else '✗'} Exact prompt match ({elapsed*1000:.2f}ms)")
    
    # Partial match
    code = "x = 5"
    start = time.time()
    result = compare_code_with_prompt(code, prompt)
    elapsed = time.time() - start
    passed = not result['similar'] or result['similarity_score'] < 0.5
    test_results.add_test("Partial prompt match", passed,
                         f"Similar: {result['similar']}, Score: {result['similarity_score']:.2f}", elapsed)
    print(f"{'✓' if passed else '✗'} Partial prompt match ({elapsed*1000:.2f}ms)")


def test_full_validation():
    """Test full validation pipeline."""
    print("\n" + "="*70)
    print("TESTING FULL VALIDATION PIPELINE")
    print("="*70)
    
    # Complete validation with multilingual code
    code = '''"""
将多个字节从一个内存位置复制到另一个内存位置。
"""
def memcpy(dest, src, num_bytes):
    # सुनिश्चित करें कि destination एक bytearray है
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest
'''
    prompt = "Write a function that copies bytes from memory"
    
    start = time.time()
    result = validate_code_for_language(code, "zh-CN", prompt)
    elapsed = time.time() - start
    
    passed = (result['status'] == 'success' and 
             result['syntax']['valid'] and 
             result['execution']['success'] and
             result['multilingual_detection']['detected'])
    
    test_results.add_test("Full validation with multilingual", passed,
                         f"Status: {result['status']}, Multilingual: {result['multilingual_detection']['detected']}", 
                         elapsed)
    print(f"{'✓' if passed else '✗'} Full validation with multilingual ({elapsed*1000:.2f}ms)")
    
    # Validation with syntax error
    code = "def test( return 42"
    start = time.time()
    result = validate_code_for_language(code, "en", None)
    elapsed = time.time() - start
    passed = result['status'] == 'syntax_error' and not result['syntax']['valid']
    test_results.add_test("Validation with syntax error", passed,
                         f"Status: {result['status']}", elapsed)
    print(f"{'✓' if passed else '✗'} Validation with syntax error ({elapsed*1000:.2f}ms)")


def test_performance_benchmark():
    """Run performance benchmarks."""
    print("\n" + "="*70)
    print("PERFORMANCE BENCHMARK")
    print("="*70)
    
    test_codes = [
        ("Simple English", "def test(): return 42"),
        ("Chinese docstring", '''def test():
    """将多个字节从一个内存位置复制到另一个内存位置。"""
    return 1'''),
        ("Multiple languages", '''def test():
    """将多个字节从一个内存位置复制到另一个内存位置。
    Copia una cantidad de bytes de una ubicación de memoria a otra."""
    # सुनिश्चित करें कि destination एक bytearray है
    return 1'''),
        ("Large code", "def test():\n" + "    # 这是注释\n" * 50 + "    return 1\n")
    ]
    
    for name, code in test_codes:
        # Multilingual detection
        times = []
        for _ in range(5):
            start = time.time()
            detect_multilingual_text(code)
            times.append(time.time() - start)
        avg_time = sum(times) / len(times)
        print(f"{name:30s} - Multilingual detection: {avg_time*1000:.2f}ms avg")
        
        # Full validation
        times = []
        for _ in range(5):
            start = time.time()
            validate_code_for_language(code, "en", None)
            times.append(time.time() - start)
        avg_time = sum(times) / len(times)
        print(f"{name:30s} - Full validation: {avg_time*1000:.2f}ms avg")


def test_reliability():
    """Test reliability and edge cases."""
    print("\n" + "="*70)
    print("TESTING RELIABILITY AND EDGE CASES")
    print("="*70)
    
    # Unicode handling
    code = '''def test():
    """测试Unicode字符处理：中文、日文、韩文、阿拉伯文"""
    return "✓✓✓"
'''
    try:
        result = detect_multilingual_text(code)
        passed = result is not None
        test_results.add_test("Unicode handling", passed, "No crash on Unicode")
        print(f"{'✓' if passed else '✗'} Unicode handling")
    except Exception as e:
        test_results.add_test("Unicode handling", False, f"Error: {str(e)}")
        print(f"✗ Unicode handling - Error: {str(e)}")
    
    # Very long strings
    long_text = "将多个字节" * 500
    code = f'def test():\n    """{long_text}"""\n    return 1'
    try:
        start = time.time()
        result = detect_multilingual_text(code)
        elapsed = time.time() - start
        passed = result is not None and elapsed < 5.0  # Should complete in reasonable time
        test_results.add_test("Very long strings", passed, f"Time: {elapsed:.2f}s", elapsed)
        print(f"{'✓' if passed else '✗'} Very long strings ({elapsed*1000:.2f}ms)")
    except Exception as e:
        test_results.add_test("Very long strings", False, f"Error: {str(e)}")
        print(f"✗ Very long strings - Error: {str(e)}")
    
    # Malformed code
    code = "def test(\n    return 42\n"
    try:
        result = detect_multilingual_text(code)
        passed = result is not None  # Should handle gracefully
        test_results.add_test("Malformed code handling", passed, "No crash on syntax error")
        print(f"{'✓' if passed else '✗'} Malformed code handling")
    except Exception as e:
        test_results.add_test("Malformed code handling", False, f"Error: {str(e)}")
        print(f"✗ Malformed code handling - Error: {str(e)}")
    
    # Empty code
    try:
        result = detect_multilingual_text("")
        passed = result is not None and not result['detected']
        test_results.add_test("Empty code handling", passed, "Handled empty code")
        print(f"{'✓' if passed else '✗'} Empty code handling")
    except Exception as e:
        test_results.add_test("Empty code handling", False, f"Error: {str(e)}")
        print(f"✗ Empty code handling - Error: {str(e)}")


def main():
    """Run all tests."""
    print("="*70)
    print("CODE VALIDATION PIPELINE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Run all test suites
    test_multilingual_detection()
    test_syntax_validation()
    test_code_execution()
    test_prompt_comparison()
    test_full_validation()
    test_reliability()
    test_performance_benchmark()
    
    # Print summary
    test_results.print_summary()
    
    # Save results to JSON
    results_file = "test_validation_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_tests': test_results.total_tests,
            'passed_tests': test_results.passed_tests,
            'failed_tests': test_results.failed_tests,
            'test_details': test_results.test_details,
            'performance_metrics': test_results.performance_metrics
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nTest results saved to: {results_file}")
    print("="*70)


if __name__ == "__main__":
    main()


