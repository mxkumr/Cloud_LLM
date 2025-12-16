"""
Test execution validity for all code files in prompt_1.

This script:
1. Imports each language's code file
2. Finds the copy function (various names)
3. Tests with a simple test case: copy bytes from source to destination
4. Reports success/failure for each language

Usage:
    python test_prompt_1_execution.py
"""

import os
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, Optional, Callable


def find_copy_function(module) -> Optional[Callable]:
    """
    Find the memory copy function in a module.
    Looks for common function names: copy_memory, memcpy, copy_bytes, memmove
    """
    function_names = ['copy_memory', 'memcpy', 'copy_bytes', 'memmove']
    
    for func_name in function_names:
        if hasattr(module, func_name):
            func = getattr(module, func_name)
            if callable(func):
                return func
    
    # If not found, look for any function that might be it
    # (functions with 'copy' or 'mem' in name)
    for attr_name in dir(module):
        if not attr_name.startswith('_'):
            attr = getattr(module, attr_name)
            if callable(attr) and ('copy' in attr_name.lower() or 'mem' in attr_name.lower()):
                return attr
    
    return None


def test_function_with_bytearray(func: Callable, func_name: str) -> Dict[str, Any]:
    """
    Test the copy function using bytearray (most common pattern).
    
    Test case:
    - Source: bytearray([1, 2, 3, 4, 5])
    - Destination: bytearray([0, 0, 0, 0, 0])
    - Copy 3 bytes
    - Expected: destination should be [1, 2, 3, 0, 0]
    """
    result = {
        'success': False,
        'error_type': None,
        'error_message': None,
        'test_passed': False
    }
    
    try:
        # Prepare test data
        source = bytearray([1, 2, 3, 4, 5])
        destination = bytearray([0, 0, 0, 0, 0])
        num_bytes = 3
        
        # Expected result
        expected = bytearray([1, 2, 3, 0, 0])
        
        # Call the function
        # Try different parameter names based on common patterns
        try:
            # Try (destination, source, num_bytes)
            return_value = func(destination, source, num_bytes)
        except TypeError:
            try:
                # Try (dest, src, n)
                return_value = func(destination, source, num_bytes)
            except TypeError:
                try:
                    # Try (source, destination, num_bytes) - reversed
                    return_value = func(source, destination, num_bytes)
                except TypeError as e:
                    result['error_type'] = 'TypeError'
                    result['error_message'] = f"Function signature mismatch: {e}"
                    return result
        
        # Check if copy was successful
        if destination == expected:
            result['success'] = True
            result['test_passed'] = True
        else:
            result['success'] = True  # Function executed without error
            result['test_passed'] = False
            result['error_message'] = f"Copy failed: expected {list(expected)}, got {list(destination)}"
        
        return result
        
    except Exception as e:
        result['error_type'] = type(e).__name__
        result['error_message'] = str(e)
        return result


def test_function_with_list(func: Callable, func_name: str) -> Dict[str, Any]:
    """
    Test the copy function using list (alternative pattern).
    """
    result = {
        'success': False,
        'error_type': None,
        'error_message': None,
        'test_passed': False
    }
    
    try:
        # Prepare test data
        source = [1, 2, 3, 4, 5]
        destination = [0, 0, 0, 0, 0]
        num_bytes = 3
        
        # Expected result
        expected = [1, 2, 3, 0, 0]
        
        # Call the function
        try:
            return_value = func(destination, source, num_bytes)
        except TypeError:
            try:
                return_value = func(destination, source, num_bytes)
            except TypeError as e:
                result['error_type'] = 'TypeError'
                result['error_message'] = f"Function signature mismatch: {e}"
                return result
        
        # Check if copy was successful
        if destination == expected:
            result['success'] = True
            result['test_passed'] = True
        else:
            result['success'] = True
            result['test_passed'] = False
            result['error_message'] = f"Copy failed: expected {expected}, got {destination}"
        
        return result
        
    except Exception as e:
        result['error_type'] = type(e).__name__
        result['error_message'] = str(e)
        return result


def test_language_file(lang_file: Path) -> Dict[str, Any]:
    """
    Test a single language code file.
    
    Returns:
        Dictionary with test results
    """
    lang_code = lang_file.stem.replace('_', '-')  # zh_CN -> zh-CN
    result = {
        'language': lang_code,
        'file': lang_file.name,
        'imported': False,
        'function_found': False,
        'function_name': None,
        'test_result': None
    }
    
    try:
        # Import the module
        spec = importlib.util.spec_from_file_location(lang_code, lang_file)
        if spec is None or spec.loader is None:
            result['error'] = 'Could not create module spec'
            return result
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[lang_code] = module  # Add to sys.modules to handle imports
        
        try:
            spec.loader.exec_module(module)
            result['imported'] = True
        except Exception as e:
            result['error'] = f'Import error: {type(e).__name__}: {e}'
            return result
        
        # Find the copy function
        func = find_copy_function(module)
        if func is None:
            result['error'] = 'No copy function found'
            return result
        
        result['function_found'] = True
        result['function_name'] = func.__name__
        
        # Test the function
        # Try bytearray first (most common)
        test_result = test_function_with_bytearray(func, func.__name__)
        
        # If bytearray fails with TypeError, try list
        if not test_result['success'] and test_result.get('error_type') == 'TypeError':
            test_result = test_function_with_list(func, func.__name__)
        
        result['test_result'] = test_result
        return result
        
    except Exception as e:
        result['error'] = f'Unexpected error: {type(e).__name__}: {e}'
        return result
    finally:
        # Clean up
        if lang_code in sys.modules:
            del sys.modules[lang_code]


def main():
    """Main entry point."""
    prompt_dir = Path("data/prompt_1")
    
    if not prompt_dir.exists():
        print(f"Error: {prompt_dir} not found")
        sys.exit(1)
    
    # Find all .py files (language files)
    lang_files = sorted([f for f in prompt_dir.glob("*.py")])
    
    if not lang_files:
        print(f"No Python files found in {prompt_dir}")
        sys.exit(1)
    
    print(f"\n{'='*70}")
    print("EXECUTION VALIDITY TEST - Prompt 1")
    print("="*70)
    print(f"Testing {len(lang_files)} language files...\n")
    
    results = []
    passed = 0
    failed = 0
    errors = 0
    
    for lang_file in lang_files:
        result = test_language_file(lang_file)
        results.append(result)
        
        # Print result
        lang = result['language']
        if result.get('error'):
            status = "✗ ERROR"
            errors += 1
            print(f"{status:12} {lang:8} | {result['error']}")
        elif not result.get('imported'):
            status = "✗ IMPORT"
            errors += 1
            print(f"{status:12} {lang:8} | Failed to import")
        elif not result.get('function_found'):
            status = "✗ NO FUNC"
            errors += 1
            print(f"{status:12} {lang:8} | No copy function found")
        elif result.get('test_result'):
            test_res = result['test_result']
            if test_res.get('test_passed'):
                status = "✓ PASS"
                passed += 1
                func_name = result.get('function_name', '?')
                print(f"{status:12} {lang:8} | {func_name}() - Test passed")
            elif test_res.get('success'):
                status = "⚠ EXEC OK"
                failed += 1
                msg = test_res.get('error_message', 'Unknown')
                print(f"{status:12} {lang:8} | Executed but test failed: {msg}")
            else:
                status = "✗ FAIL"
                failed += 1
                error_type = test_res.get('error_type', 'Unknown')
                error_msg = test_res.get('error_message', 'Unknown error')
                print(f"{status:12} {lang:8} | {error_type}: {error_msg}")
        else:
            status = "✗ UNKNOWN"
            errors += 1
            print(f"{status:12} {lang:8} | Unknown error")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    print(f"Total files tested: {len(lang_files)}")
    print(f"✓ Passed:  {passed}")
    print(f"⚠ Exec OK (test failed): {failed}")
    print(f"✗ Errors:  {errors}")
    print(f"Success rate: {(passed / len(lang_files) * 100):.1f}%")
    print("="*70)
    
    # Detailed results for failures
    if failed > 0 or errors > 0:
        print("\nDETAILED FAILURES:")
        for result in results:
            if result.get('error') or (result.get('test_result') and not result['test_result'].get('test_passed')):
                print(f"\n  {result['language']} ({result['file']}):")
                if result.get('error'):
                    print(f"    Error: {result['error']}")
                elif result.get('test_result'):
                    tr = result['test_result']
                    print(f"    Function: {result.get('function_name', '?')}")
                    print(f"    Error Type: {tr.get('error_type', 'N/A')}")
                    print(f"    Message: {tr.get('error_message', 'N/A')}")


if __name__ == "__main__":
    main()

