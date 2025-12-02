"""
Code Validation Pipeline

This pipeline validates generated code by:
1. Executing code and checking for runtime errors
2. Analyzing if the code understood the prompt
3. Checking if the code is relevant to the prompt
4. Detecting spoken languages in code with locations and instances

Usage:
    # Process all prompts in data/ directory
    python code_validation_pipeline.py
    
    # Process a specific prompt directory
    python code_validation_pipeline.py data/prompt_1
"""

import os
import sys
import json
import tempfile
import subprocess
import traceback
import ast
import re
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import importlib.util


def ensure_mlp_on_path(project_root: str) -> str:
    """Ensure Multi_language_parser is on Python path."""
    mlp_dir = os.path.join(project_root, "Multi_language_parser")
    if mlp_dir not in sys.path:
        sys.path.insert(0, mlp_dir)
    return mlp_dir


def detect_languages_in_code(code: str, code_language: str = "python") -> Dict[str, List[Dict[str, Any]]]:
    """
    Detect spoken languages in code with locations and instances.
    
    Returns:
        Dictionary mapping language names to lists of instances with:
        - text: the detected text
        - location: line number or location description
        - category: comment, docstring, string_literal, identifier, etc.
        - confidence: detection confidence
    """
    from language_detection import classify_string
    
    results = defaultdict(list)
    
    try:
        # Parse Python code to extract different elements
        if code_language == "python":
            tree = ast.parse(code)
            
            # Extract docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    docstring = ast.get_docstring(node)
                    if docstring:
                        classification = classify_string(docstring)
                        if classification['script'] != 'English/ASCII':
                            results[classification['script']].append({
                                'text': docstring,
                                'location': f"Line {node.lineno} (docstring)",
                                'category': 'docstring',
                                'confidence': classification.get('confidence', 1.0)
                            })
            
            # Extract string literals
            for node in ast.walk(tree):
                if isinstance(node, ast.Str):
                    text = node.s
                    if text and len(text) > 2:  # Skip very short strings
                        classification = classify_string(text)
                        if classification['script'] != 'English/ASCII':
                            results[classification['script']].append({
                                'text': text[:100],  # Truncate long strings
                                'location': f"Line {node.lineno} (string literal)",
                                'category': 'string_literal',
                                'confidence': classification.get('confidence', 1.0)
                            })
        
        # Extract comments (works for any language)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Python comments
            if '#' in line:
                comment = line.split('#', 1)[1].strip()
                if comment:
                    classification = classify_string(comment)
                    if classification['script'] != 'English/ASCII':
                        results[classification['script']].append({
                            'text': comment[:100],
                            'location': f"Line {i} (comment)",
                            'category': 'comment',
                            'confidence': classification.get('confidence', 1.0)
                        })
            
            # Multi-line comments (for other languages)
            if '"""' in line or "'''" in line:
                # This is a simplified check; full parsing would be better
                pass
        
        # Check identifiers (variable names, function names)
        # Extract identifiers using regex
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_\u0080-\uFFFF]*\b'
        for match in re.finditer(identifier_pattern, code):
            identifier = match.group()
            # Skip if it's all ASCII
            if identifier.encode('ascii', 'ignore').decode('ascii') != identifier:
                classification = classify_string(identifier)
                if classification['script'] != 'English/ASCII':
                    # Find line number
                    line_num = code[:match.start()].count('\n') + 1
                    results[classification['script']].append({
                        'text': identifier,
                        'location': f"Line {line_num} (identifier)",
                        'category': 'identifier',
                        'confidence': classification.get('confidence', 1.0)
                    })
    
    except Exception as e:
        # If parsing fails, do a simple text-based search
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            classification = classify_string(line)
            if classification['script'] != 'English/ASCII':
                results[classification['script']].append({
                    'text': line[:100],
                    'location': f"Line {i}",
                    'category': 'unknown',
                    'confidence': classification.get('confidence', 1.0)
                })
    
    return dict(results)


def execute_code(code: str, code_language: str = "python", timeout: int = 10) -> Dict[str, Any]:
    """
    Execute code and check for runtime errors.
    
    Returns:
        Dictionary with:
        - success: bool
        - error_type: str (None if success)
        - error_message: str (None if success)
        - execution_time: float (seconds)
        - output: str (stdout if any)
    """
    result = {
        'success': False,
        'error_type': None,
        'error_message': None,
        'execution_time': 0.0,
        'output': None
    }
    
    if not code or not code.strip():
        result['error_type'] = 'EmptyCode'
        result['error_message'] = 'Code is empty'
        return result
    
    if code_language == "python":
        # First, check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            result['error_type'] = 'SyntaxError'
            result['error_message'] = f"Line {e.lineno}: {e.msg}"
            return result
        except Exception as e:
            result['error_type'] = 'ParseError'
            result['error_message'] = str(e)
            return result
        
        # Try to execute the code
        try:
            import time
            start_time = time.time()
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                process = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace'
                )
                
                result['execution_time'] = time.time() - start_time
                result['output'] = process.stdout
                
                if process.returncode == 0:
                    result['success'] = True
                else:
                    result['error_type'] = 'RuntimeError'
                    result['error_message'] = process.stderr or "Non-zero exit code"
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            result['error_type'] = 'TimeoutError'
            result['error_message'] = f'Code execution exceeded {timeout} seconds'
        except Exception as e:
            result['error_type'] = 'ExecutionError'
            result['error_message'] = str(e)
            result['execution_time'] = time.time() - start_time if 'start_time' in locals() else 0.0
    
    return result


def check_prompt_understanding(code: str, prompt: str, model_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Check if the code understood the prompt using semantic analysis.
    
    Uses a simple heuristic approach (can be enhanced with LLM-based analysis).
    
    Returns:
        Dictionary with:
        - understood: bool
        - confidence: float (0-1)
        - reasoning: str
        - missing_elements: List[str]
    """
    result = {
        'understood': False,
        'confidence': 0.0,
        'reasoning': '',
        'missing_elements': []
    }
    
    # Extract key requirements from prompt (simple keyword extraction)
    prompt_lower = prompt.lower()
    code_lower = code.lower()
    
    # Common programming keywords that should appear if prompt was understood
    key_terms = []
    if 'function' in prompt_lower:
        key_terms.append('def')
    if 'class' in prompt_lower:
        key_terms.append('class')
    if 'copy' in prompt_lower or 'memory' in prompt_lower:
        key_terms.extend(['copy', 'memcpy', 'memory'])
    if 'array' in prompt_lower:
        key_terms.append('array')
    if 'string' in prompt_lower:
        key_terms.append('string')
    
    # Check if key terms appear in code
    found_terms = [term for term in key_terms if term in code_lower]
    missing_terms = [term for term in key_terms if term not in code_lower]
    
    if missing_terms:
        result['missing_elements'] = missing_terms
    
    # Calculate confidence based on found terms
    if key_terms:
        confidence = len(found_terms) / len(key_terms)
    else:
        confidence = 0.5  # Default if no clear keywords
    
    result['confidence'] = confidence
    result['understood'] = confidence >= 0.5
    
    if result['understood']:
        result['reasoning'] = f"Code appears to address the prompt (found {len(found_terms)}/{len(key_terms)} key terms)"
    else:
        result['reasoning'] = f"Code may not fully address the prompt (missing: {', '.join(missing_terms)})"
    
    return result


def check_code_relevance(code: str, prompt: str) -> Dict[str, Any]:
    """
    Check if the code is relevant to the prompt.
    
    Uses semantic similarity and keyword matching.
    
    Returns:
        Dictionary with:
        - relevant: bool
        - relevance_score: float (0-1)
        - reasoning: str
    """
    result = {
        'relevant': False,
        'relevance_score': 0.0,
        'reasoning': ''
    }
    
    # Extract action verbs and nouns from prompt
    prompt_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower()))
    code_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', code.lower()))
    
    # Remove common stop words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'way', 'use', 'def', 'import', 'from', 'return', 'class', 'self'}
    prompt_words = prompt_words - stop_words
    code_words = code_words - stop_words
    
    # Calculate overlap
    if prompt_words:
        overlap = len(prompt_words & code_words)
        relevance_score = overlap / len(prompt_words)
    else:
        relevance_score = 0.5
    
    result['relevance_score'] = relevance_score
    result['relevant'] = relevance_score >= 0.3  # Threshold
    
    if result['relevant']:
        result['reasoning'] = f"Code shows {relevance_score:.1%} semantic overlap with prompt"
    else:
        result['reasoning'] = f"Code shows low semantic overlap ({relevance_score:.1%}) with prompt"
    
    return result


def validate_code_for_language(code: str, prompt: str, language_key: str, 
                               code_language: str = "python") -> Dict[str, Any]:
    """
    Complete validation for a single code snippet.
    
    Returns comprehensive validation results.
    """
    validation_result = {
        'language': language_key,
        'code_length': len(code),
        'execution': execute_code(code, code_language),
        'prompt_understanding': check_prompt_understanding(code, prompt),
        'code_relevance': check_code_relevance(code, prompt),
        'language_detection': detect_languages_in_code(code, code_language)
    }
    
    # Overall score
    scores = []
    if validation_result['execution']['success']:
        scores.append(1.0)
    else:
        scores.append(0.0)
    
    scores.append(validation_result['prompt_understanding']['confidence'])
    scores.append(validation_result['code_relevance']['relevance_score'])
    
    validation_result['overall_score'] = sum(scores) / len(scores) if scores else 0.0
    
    return validation_result


def process_prompt_directory(prompt_dir: str, project_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Process all code in a prompt directory and generate validation results.
    
    Args:
        prompt_dir: Path to prompt directory (e.g., data/prompt_1)
        project_root: Optional project root path
    
    Returns:
        Dictionary with validation results for all languages
    """
    if project_root is None:
        project_root = os.path.abspath(os.path.dirname(__file__))
    
    ensure_mlp_on_path(project_root)
    
    # Load required files
    llm_output_path = os.path.join(prompt_dir, "llm_output.json")
    translated_prompts_path = os.path.join(prompt_dir, "translated_prompts.json")
    
    if not os.path.exists(llm_output_path):
        raise FileNotFoundError(f"llm_output.json not found in {prompt_dir}")
    
    with open(llm_output_path, 'r', encoding='utf-8') as f:
        llm_outputs = json.load(f)
    
    # Get original prompt (use English translation as reference)
    original_prompt = None
    if os.path.exists(translated_prompts_path):
        with open(translated_prompts_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            original_prompt = translations.get('en', '')
    
    if not original_prompt:
        # Try to get from prompts_input.json
        prompts_input_path = os.path.join(project_root, "prompts_input.json")
        if os.path.exists(prompts_input_path):
            with open(prompts_input_path, 'r', encoding='utf-8') as f:
                prompts_data = json.load(f)
                prompt_id = os.path.basename(prompt_dir)
                for prompt in prompts_data.get('prompts', []):
                    if prompt.get('id') == prompt_id:
                        original_prompt = prompt.get('text', '')
                        break
    
    if not original_prompt:
        original_prompt = "Unknown prompt"
    
    # Validate each code snippet
    validation_results = {}
    for lang_key, code in llm_outputs.items():
        if not code:
            validation_results[lang_key] = {
                'language': lang_key,
                'error': 'No code provided',
                'overall_score': 0.0
            }
            continue
        
        print(f"Validating code for {lang_key}...")
        try:
            validation_results[lang_key] = validate_code_for_language(
                code, original_prompt, lang_key
            )
        except Exception as e:
            validation_results[lang_key] = {
                'language': lang_key,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'overall_score': 0.0
            }
    
    # Create summary
    summary = {
        'total_languages': len(validation_results),
        'successful_executions': sum(1 for r in validation_results.values() 
                                     if r.get('execution', {}).get('success', False)),
        'average_overall_score': sum(r.get('overall_score', 0.0) for r in validation_results.values()) / len(validation_results) if validation_results else 0.0,
        'languages_with_errors': [k for k, v in validation_results.items() 
                                 if not v.get('execution', {}).get('success', True)],
        'languages_with_non_english': [k for k, v in validation_results.items() 
                                      if v.get('language_detection', {})]
    }
    
    return {
        'prompt_directory': prompt_dir,
        'original_prompt': original_prompt,
        'summary': summary,
        'detailed_results': validation_results,
        'generated_at': __import__('datetime').datetime.now().isoformat()
    }


def find_prompt_folders(data_dir: str) -> List[str]:
    """
    Find all prompt folders in the data directory.
    Returns a list of folder paths that contain llm_output.json.
    """
    prompt_folders = []
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return prompt_folders
    
    # Scan all subdirectories in data/
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        
        # Check if it's a directory and contains llm_output.json
        if os.path.isdir(item_path):
            llm_output_path = os.path.join(item_path, "llm_output.json")
            if os.path.exists(llm_output_path):
                prompt_folders.append(item_path)
    
    # Sort folders for consistent processing order
    prompt_folders.sort()
    return prompt_folders


def process_single_prompt_validation(prompt_dir: str, project_root: str) -> bool:
    """
    Process validation for a single prompt directory.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\nProcessing validation for: {os.path.basename(prompt_dir)}")
        print("=" * 60)
        
        results = process_prompt_directory(prompt_dir, project_root)
        
        # Save results
        output_path = os.path.join(prompt_dir, "code_validation.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Validation complete for {os.path.basename(prompt_dir)}")
        print(f"  - Total languages: {results['summary']['total_languages']}")
        print(f"  - Successful executions: {results['summary']['successful_executions']}")
        print(f"  - Average score: {results['summary']['average_overall_score']:.2%}")
        print(f"  - Results saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error processing {os.path.basename(prompt_dir)}: {e}")
        traceback.print_exc()
        return False


def main():
    """Main entry point for the validation pipeline."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    
    # Check if a specific prompt directory was provided
    if len(sys.argv) >= 2:
        # Process single prompt directory
        prompt_dir = sys.argv[1]
        if not os.path.isabs(prompt_dir):
            prompt_dir = os.path.join(project_root, prompt_dir)
        
        if not os.path.exists(prompt_dir):
            print(f"Error: Directory not found: {prompt_dir}")
            sys.exit(1)
        
        print(f"Processing validation for: {prompt_dir}")
        print("=" * 60)
        
        try:
            results = process_prompt_directory(prompt_dir, project_root)
            
            # Save results
            output_path = os.path.join(prompt_dir, "code_validation.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print("\n" + "=" * 60)
            print("VALIDATION SUMMARY")
            print("=" * 60)
            print(f"Total languages processed: {results['summary']['total_languages']}")
            print(f"Successful executions: {results['summary']['successful_executions']}")
            print(f"Average overall score: {results['summary']['average_overall_score']:.2%}")
            print(f"Languages with errors: {len(results['summary']['languages_with_errors'])}")
            print(f"Languages with non-English text: {len(results['summary']['languages_with_non_english'])}")
            print(f"\nResults saved to: {output_path}")
            
            # Print detailed results for languages with issues
            if results['summary']['languages_with_errors']:
                print("\nLanguages with execution errors:")
                for lang in results['summary']['languages_with_errors']:
                    error = results['detailed_results'][lang].get('execution', {})
                    print(f"  - {lang}: {error.get('error_type')} - {error.get('error_message', '')[:50]}")
            
            # Print languages with non-English content
            if results['summary']['languages_with_non_english']:
                print("\nLanguages with non-English text detected:")
                for lang in results['summary']['languages_with_non_english']:
                    detections = results['detailed_results'][lang].get('language_detection', {})
                    for script, instances in detections.items():
                        print(f"  - {lang}: {script} ({len(instances)} instances)")
                        for instance in instances[:3]:  # Show first 3
                            print(f"      {instance['location']}: {instance['text'][:50]}...")
            
        except Exception as e:
            print(f"Error processing validation: {e}")
            traceback.print_exc()
            sys.exit(1)
    else:
        # Process all prompt directories in data/
        print(f"\n{'='*60}")
        print("Code Validation Pipeline - Batch Processing")
        print("="*60)
        print(f"Scanning data directory: {data_dir}")
        
        # Find all prompt folders
        prompt_folders = find_prompt_folders(data_dir)
        
        if not prompt_folders:
            print(f"\nNo prompt folders with llm_output.json found in {data_dir}")
            print("Please ensure you have run pipeline.py first to generate llm_output.json files")
            sys.exit(1)
        
        print(f"\nFound {len(prompt_folders)} prompt folder(s) to process:")
        for folder in prompt_folders:
            print(f"  - {os.path.basename(folder)}")
        
        # Process each folder
        successful = 0
        failed = 0
        
        for i, prompt_dir in enumerate(prompt_folders, 1):
            print(f"\n{'='*60}")
            print(f"Processing folder {i}/{len(prompt_folders)}: {os.path.basename(prompt_dir)}")
            print(f"{'='*60}")
            
            if process_single_prompt_validation(prompt_dir, project_root):
                successful += 1
            else:
                failed += 1
        
        # Summary
        print(f"\n{'='*60}")
        print("BATCH PROCESSING COMPLETE!")
        print(f"{'='*60}")
        print(f"Successfully processed: {successful}/{len(prompt_folders)} folders")
        if failed > 0:
            print(f"Failed: {failed} folder(s)")
        print(f"\nResults saved in individual folders under: {data_dir}")
        print(f"Each folder contains: code_validation.json")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

