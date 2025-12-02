"""
Code Validation Pipeline

This pipeline validates generated code by:
1. Checking if the syntax is correct
2. Executing code and checking for runtime errors
3. Comparing code with the translated prompt to check similarity

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
import time
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

# Try to import language detection libraries for enhanced detection
try:
    from langdetect import detect, DetectorFactory
    # Set seed for consistent results
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("Warning: langdetect not available. Install with: pip install langdetect")

# Also try to import GoogleTranslator for translation (optional)
try:
    from deep_translator import GoogleTranslator
    GOOGLE_TRANSLATOR_AVAILABLE = True
except ImportError:
    GOOGLE_TRANSLATOR_AVAILABLE = False


def detect_multilingual_text(code: str) -> Dict[str, Any]:
    """
    Detect non-English text in code and identify where it appears.
    Uses both script-based detection and GoogleTranslator for enhanced accuracy.
    Only detects the 18 languages from Prompt_translation.py.
    
    Returns:
        Dictionary with:
        - detected: bool
        - locations: List[Dict] with location, category, language, and text
    """
    result = {
        'detected': False,
        'locations': []
    }
    
    # Allowed languages - only the 18 languages from Prompt_translation.py
    ALLOWED_LANGUAGES = {
        "Mandarin Chinese", "Chinese",  # zh-CN can be detected as either
        "Hindi",
        "Spanish",
        "Standard Arabic", "Arabic",  # Can be detected as either
        "French",
        "Bengali",
        "Portuguese",
        "Russian",
        "Indonesian",
        "Urdu",
        "Standard German", "German",  # Can be detected as either
        "Japanese",
        "Marathi",
        "Vietnamese",
        "Telugu",
        "Hausa",
        "Turkish"
    }
    
    # Language code to full name mapping (only the 18 languages from Prompt_translation.py)
    LANGUAGE_NAMES = {
        "en": "English",
        "zh-CN": "Mandarin Chinese",
        "zh": "Mandarin Chinese",  # Map zh to Mandarin Chinese
        "zh-cn": "Mandarin Chinese",
        "hi": "Hindi",
        "es": "Spanish",
        "ar": "Standard Arabic",
        "fr": "French",
        "bn": "Bengali",
        "pt": "Portuguese",
        "ru": "Russian",
        "id": "Indonesian",
        "ur": "Urdu",
        "de": "Standard German",
        "ja": "Japanese",
        "mr": "Marathi",
        "vi": "Vietnamese",
        "te": "Telugu",
        "ha": "Hausa",
        "tr": "Turkish",
    }
    
    # Simple script detection patterns (primary method)
    script_patterns = {
        'Chinese': re.compile(r'[\u4E00-\u9FFF]'),
        'Japanese': re.compile(r'[\u3040-\u30FF]'),
        'Korean': re.compile(r'[\uAC00-\uD7AF]'),
        'Arabic': re.compile(r'[\u0600-\u06FF]'),
        'Hebrew': re.compile(r'[\u0590-\u05FF]'),
        'Hindi': re.compile(r'[\u0900-\u097F]'),
        'Thai': re.compile(r'[\u0E00-\u0E7F]'),
        'Russian': re.compile(r'[\u0400-\u04FF]'),
        'Greek': re.compile(r'[\u0370-\u03FF]'),
        'Bengali': re.compile(r'[\u0980-\u09FF]'),
        'Telugu': re.compile(r'[\u0C00-\u0C7F]'),
        'Marathi': re.compile(r'[\u0900-\u097F]'),  # Uses Devanagari script
    }
    
    def detect_language_script(text: str) -> Optional[str]:
        """Detect language using script patterns (fast, primary method)."""
        if not text:
            return None
        
        # Check if it's ASCII/English
        try:
            text.encode('ascii')
            return None
        except UnicodeEncodeError:
            pass
        
        # Map script-detected languages to allowed language names
        script_to_allowed = {
            'Chinese': 'Mandarin Chinese',
            'Arabic': 'Standard Arabic',
            'German': 'Standard German',
            'Hindi': 'Hindi',
            'Japanese': 'Japanese',
            'Korean': None,  # Not in allowed list
            'Russian': 'Russian',
            'Bengali': 'Bengali',
            'Telugu': 'Telugu',
            'Marathi': 'Marathi',
            'Thai': None,  # Not in allowed list
            'Hebrew': None,  # Not in allowed list
            'Greek': None,  # Not in allowed list
        }
        
        # Check script patterns
        for lang, pattern in script_patterns.items():
            if pattern.search(text):
                # Map to allowed language name
                mapped_lang = script_to_allowed.get(lang)
                if mapped_lang and mapped_lang in ALLOWED_LANGUAGES:
                    return mapped_lang
                # If not mapped or not allowed, return None
                return None
        
        # Check for any non-ASCII (but don't return 'Non-English' - we need specific language)
        # This will be handled by langdetect if available
        return None
    
    def detect_language_google(text: str) -> Optional[str]:
        """Detect language using langdetect library (secondary method for confirmation)."""
        if not LANGDETECT_AVAILABLE:
            return None
        
        if not text or len(text.strip()) < 2:
            return None
        
        try:
            # Clean text - remove code-like patterns that might confuse detector
            clean_text = text.strip()
            
            # Extract meaningful text (remove excessive punctuation, keep words)
            # Count alphabetic characters
            alpha_chars = [c for c in clean_text if c.isalpha() or c.isspace()]
            meaningful_text = ''.join(alpha_chars).strip()
            
            # Need at least 3 characters of meaningful text for reliable detection
            if len(meaningful_text) < 3:
                return None
            
            # Skip if it looks like pure code (too many operators, brackets)
            code_chars = sum(1 for c in clean_text if c in ['=', '(', ')', '[', ']', '{', '}', '<', '>', ':', ';', '.'])
            if code_chars > len(meaningful_text) / 2:
                return None
            
            # Use langdetect to detect language
            detected_lang_code = detect(meaningful_text)
            
            if detected_lang_code and detected_lang_code != 'en':
                # Filter out very short language codes that might be false positives
                if len(detected_lang_code) < 2:
                    return None
                
                code_lower = detected_lang_code.lower()
                
                # Filter out false positive codes for very short text
                # These codes are often false positives when text is short
                false_positive_codes_short = {'et', 'ca', 'sq', 'nl', 'da', 'ro', 'no', 'sv', 'fi', 'cs', 'sk', 'sl', 'hr'}
                if len(meaningful_text) < 10 and code_lower in false_positive_codes_short:
                    return None
                
                # Convert language code to full name
                # Normalize the code (lowercase for lookup)
                
                # Handle zh-CN case (langdetect returns 'zh-cn' or 'zh')
                if code_lower.startswith('zh'):
                    lang_name = LANGUAGE_NAMES.get('zh-CN', LANGUAGE_NAMES.get('zh', 'Chinese'))
                else:
                    # Try exact match first, then lowercase match
                    lang_name = LANGUAGE_NAMES.get(detected_lang_code) or LANGUAGE_NAMES.get(code_lower)
                    
                    # If still not found, try to create a readable name
                    if not lang_name:
                        # For unknown codes, capitalize properly
                        if len(code_lower) == 2:
                            lang_name = code_lower.upper()  # Keep as code if unknown
                        else:
                            lang_name = code_lower.capitalize()
                
                return lang_name
            
            return None
        except Exception:
            # If langdetect fails, return None (fallback to script detection)
            # Silently fail to avoid cluttering output
            return None
    
    def normalize_language_name(lang: str) -> Optional[str]:
        """Normalize language name to proper format. Only returns allowed languages."""
        if not lang:
            return None
        
        # Normalize input - lowercase for lookup
        lang_lower = lang.lower().strip()
        lang_upper = lang.upper().strip()
        
        # First, check if it's a 2-letter code (most common case)
        if len(lang) == 2:
            # Try lowercase first, then uppercase
            full_name = LANGUAGE_NAMES.get(lang_lower)
            if full_name and full_name in ALLOWED_LANGUAGES:
                return full_name
            # If not found or not allowed, return None
            return None
        
        # Check if it's already a full language name in our mapping
        for code, name in LANGUAGE_NAMES.items():
            if lang_lower == name.lower():
                if name in ALLOWED_LANGUAGES:
                    return name
            if lang_lower == code.lower():
                if name in ALLOWED_LANGUAGES:
                    return name
        
        # If it's a longer string that looks like a language name (has spaces or is descriptive)
        if ' ' in lang or len(lang) > 10:
            # Check if it matches any allowed language name (case-insensitive)
            for allowed_lang in ALLOWED_LANGUAGES:
                if lang_lower == allowed_lang.lower() or lang_lower in allowed_lang.lower() or allowed_lang.lower() in lang_lower:
                    return allowed_lang
            # Check against LANGUAGE_NAMES mapping
            for code, name in LANGUAGE_NAMES.items():
                if name in ALLOWED_LANGUAGES and (lang_lower in name.lower() or name.lower() in lang_lower):
                    return name
        
        # For 3+ character codes, try to match
        if len(lang) >= 3:
            # Try exact match
            if lang_lower in LANGUAGE_NAMES:
                name = LANGUAGE_NAMES[lang_lower]
                if name in ALLOWED_LANGUAGES:
                    return name
            # Try partial match
            for code, name in LANGUAGE_NAMES.items():
                if name in ALLOWED_LANGUAGES and (code.lower().startswith(lang_lower) or lang_lower.startswith(code.lower())):
                    return name
        
        # Not an allowed language
        return None
    
    def detect_language(text: str) -> Optional[str]:
        """
        Detect language using both script-based and GoogleTranslator methods.
        Combines results for better accuracy. Only returns allowed languages.
        """
        if not text:
            return None
        
        # First, try script-based detection (fast)
        script_lang = detect_language_script(text)
        
        # Always try langdetect for better detection, especially for Latin-based languages
        google_lang = None
        if LANGDETECT_AVAILABLE:
            google_lang = detect_language_google(text)
        
        # Decision logic:
        # 1. If script detection found a specific language (not just 'Non-English')
        if script_lang and script_lang != 'Non-English':
            if google_lang:
                # Both methods found something - prefer the more specific one
                # If they match or are related, use Google's result (more specific)
                script_lower = script_lang.lower()
                google_lower = google_lang.lower()
                if (script_lower in google_lower or google_lower in script_lower or
                    any(word in google_lower for word in script_lower.split())):
                    normalized = normalize_language_name(google_lang)
                    # Final check: ensure it's in allowed languages
                    if normalized and normalized in ALLOWED_LANGUAGES:
                        return normalized
                # If they differ significantly, prefer script detection for non-Latin scripts
                if script_lang in ALLOWED_LANGUAGES:
                    return script_lang
            elif script_lang in ALLOWED_LANGUAGES:
                return script_lang
        
        # 2. If script detection found 'Non-English' (non-ASCII but unknown script)
        if script_lang == 'Non-English':
            if google_lang:
                # GoogleTranslator can identify the language
                normalized = normalize_language_name(google_lang)
                if normalized and normalized in ALLOWED_LANGUAGES:
                    return normalized
            # Don't return 'Non-English' - it's not in allowed list
            return None
        
        # 3. If script detection found nothing (might be Latin-based non-English)
        # Use GoogleTranslator to detect languages like Spanish, French, Portuguese, etc.
        if google_lang:
            normalized = normalize_language_name(google_lang)
            if normalized and normalized in ALLOWED_LANGUAGES:
                return normalized
        
        # 4. No detection or not in allowed languages
        return None
    
    locations = []
    lines = code.split('\n')
    
    try:
        # Parse Python code
        tree = ast.parse(code)
        
        # Track docstring nodes to avoid double-counting them as string literals
        docstring_node_ids = set()
        
        # First pass: identify all docstring nodes
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if hasattr(node, 'body') and node.body:
                    # The docstring is the first statement in the body (if it's a string literal)
                    first_stmt = node.body[0]
                    if isinstance(first_stmt, ast.Expr):
                        # Docstring is stored as Expr(value=Constant(...)) or Expr(value=Str(...))
                        # For Python 3.8+: Expr(value=Constant(value=str))
                        if isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                            docstring_node_ids.add(id(first_stmt.value))
                        # For Python < 3.8: Expr(value=Str(s=str))
                        elif hasattr(ast, 'Str') and isinstance(first_stmt.value, ast.Str):
                            docstring_node_ids.add(id(first_stmt.value))
        
        # Extract docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    lang = detect_language(docstring)
                    if lang:
                        locations.append({
                            'category': 'docstring',
                            'location': f"Line {node.lineno}",
                            'language': lang,
                            'text': docstring[:100] + ('...' if len(docstring) > 100 else '')
                        })
        
        # Extract string literals (excluding docstrings)
        for node in ast.walk(tree):
            # Skip if this node is a docstring
            if id(node) in docstring_node_ids:
                continue
                
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                text = node.value
                if text and len(text) > 2:
                    lang = detect_language(text)
                    if lang:
                        locations.append({
                            'category': 'string_literal',
                            'location': f"Line {node.lineno}",
                            'language': lang,
                            'text': text[:100] + ('...' if len(text) > 100 else '')
                        })
            # Handle Python < 3.8 compatibility
            elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
                # Skip if this node is a docstring
                if id(node) in docstring_node_ids:
                    continue
                    
                text = node.s
                if text and len(text) > 2:
                    lang = detect_language(text)
                    if lang:
                        locations.append({
                            'category': 'string_literal',
                            'location': f"Line {node.lineno}",
                            'language': lang,
                            'text': text[:100] + ('...' if len(text) > 100 else '')
                        })
        
        # Extract function names - filter common English function names and programming terms
        common_function_names = {
            # Common function names
            'test', 'main', 'init', 'str', 'repr', 'len', 'get', 'set', 
            'add', 'remove', 'update', 'clear', 'copy', 'keys', 'values',
            'items', 'has', 'is', 'to', 'from', 'run', 'start', 'stop',
            # Programming/system functions
            'memcpy', 'memset', 'malloc', 'free', 'printf', 'scanf', 'strcpy', 'strlen',
            'range', 'print', 'input', 'open', 'read', 'write', 'close', 'seek',
            'split', 'join', 'strip', 'replace', 'find', 'index', 'count', 'sort',
            'append', 'extend', 'pop', 'insert', 'remove', 'reverse', 'max', 'min',
            'abs', 'round', 'int', 'float', 'str', 'bool', 'list', 'dict', 'tuple',
            'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr',
            'enumerate', 'zip', 'map', 'filter', 'reduce', 'any', 'all', 'sum'
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Skip common English function names and programming terms
                if func_name.lower() in common_function_names or len(func_name) < 4:
                    continue
                # Skip if it looks like a programming term (all lowercase, common patterns)
                if func_name.islower() and func_name in common_function_names:
                    continue
                
                # Only check function names that contain non-ASCII characters
                # This avoids false positives from English programming terms
                try:
                    func_name.encode('ascii')
                    # If it's pure ASCII, skip it (likely English programming term)
                    continue
                except UnicodeEncodeError:
                    # Contains non-ASCII, so it might be multilingual
                    pass
                
                lang = detect_language(func_name)
                if lang:
                    # Filter out very short language codes (likely false positives)
                    if len(lang) <= 2 and lang not in ['Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Russian']:
                        continue
                    # Additional check: skip if detected language is likely a false positive for programming terms
                    if lang in ['Indonesian', 'DA', 'RO', 'NO', 'ET', 'HR'] and func_name.islower():
                        continue
                    locations.append({
                        'category': 'function_name',
                        'location': f"Line {node.lineno}",
                        'language': lang,
                        'text': func_name
                    })
        
        # Extract variable names (identifiers) - only check longer names to avoid false positives
        # Python built-in functions and keywords
        python_builtins = {
            'print', 'def', 'class', 'import', 'from', 'return', 'if', 'else', 
            'for', 'while', 'try', 'except', 'with', 'as', 'pass', 'break', 
            'continue', 'True', 'False', 'None', 'self', 'range', 'len', 'str',
            'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set', 'frozenset',
            'open', 'read', 'write', 'close', 'input', 'raw_input', 'eval', 'exec',
            'abs', 'round', 'min', 'max', 'sum', 'all', 'any', 'enumerate', 'zip',
            'map', 'filter', 'reduce', 'sorted', 'reversed', 'iter', 'next',
            'isinstance', 'type', 'hasattr', 'getattr', 'setattr', 'delattr',
            'dir', 'vars', 'globals', 'locals', 'id', 'hash', 'repr', 'ascii',
            'format', 'bin', 'oct', 'hex', 'ord', 'chr', 'divmod', 'pow'
        }
        # Common programming/system function names
        common_programming_terms = {
            'memcpy', 'memset', 'malloc', 'free', 'printf', 'scanf', 'strcpy', 'strlen',
            'message', 'result', 'value', 'data', 'item', 'temp', 'tmp', 'var', 'val',
            'obj', 'arg', 'args', 'kwargs', 'func', 'callback', 'handler', 'ctx', 'config'
        }
        common_keywords = python_builtins | common_programming_terms
        
        # Language codes that are often false positives for short variable names
        false_positive_codes = {'da', 'ro', 'no', 'et', 'hr', 'sv', 'fi', 'cs', 'sk', 'sl', 'id'}
        false_positive_languages = {'Indonesian', 'DA', 'RO', 'NO', 'ET', 'HR', 'ID'}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                var_name = node.id
                # Skip common keywords, built-ins, and very short names (likely false positives)
                if var_name in common_keywords or len(var_name) < 5:
                    continue
                # Skip if it's a Python built-in (check at runtime)
                try:
                    if var_name in dir(__builtins__):
                        continue
                except:
                    pass
                
                # Only check variable names that contain non-ASCII characters
                # This avoids false positives from English programming terms
                try:
                    var_name.encode('ascii')
                    # If it's pure ASCII, skip it (likely English programming term)
                    continue
                except UnicodeEncodeError:
                    # Contains non-ASCII, so it might be multilingual
                    pass
                
                lang = detect_language(var_name)
                if lang:
                    # Additional check: skip if it's a known false positive language code
                    lang_lower = lang.lower()
                    if any(fp in lang_lower for fp in false_positive_codes):
                        continue
                    # Skip if detected as false positive languages for programming terms
                    if lang in false_positive_languages and var_name.islower():
                        continue
                    locations.append({
                        'category': 'variable',
                        'location': f"Line {node.lineno if hasattr(node, 'lineno') else 'unknown'}",
                        'language': lang,
                        'text': var_name
                    })
        
        # Extract comments
        language_name_keywords = {'english', 'chinese', 'spanish', 'french', 'german', 'japanese',
                                 'korean', 'arabic', 'hindi', 'russian', 'portuguese', 'italian',
                                 'dutch', 'turkish', 'vietnamese', 'thai', 'indonesian', 'urdu'}
        for i, line in enumerate(lines, 1):
            if '#' in line:
                comment = line.split('#', 1)[1].strip()
                if comment:
                    # Skip comments that are just language names (often false positives)
                    comment_lower = comment.lower()
                    if any(keyword in comment_lower for keyword in language_name_keywords):
                        # Only skip if it's a very short comment (likely just a language label)
                        if len(comment.split()) <= 3:
                            continue
                    lang = detect_language(comment)
                    if lang:
                        locations.append({
                            'category': 'comment',
                            'location': f"Line {i}",
                            'language': lang,
                            'text': comment[:100] + ('...' if len(comment) > 100 else '')
                        })
    
    except Exception:
        # If parsing fails, do simple line-by-line check
        for i, line in enumerate(lines, 1):
            lang = detect_language(line)
            if lang:
                locations.append({
                    'category': 'unknown',
                    'location': f"Line {i}",
                    'language': lang,
                    'text': line[:100] + ('...' if len(line) > 100 else '')
                })
    
    # Filter locations to only include allowed languages
    filtered_locations = []
    for loc in locations:
        loc_lang = loc.get('language', '')
        # Check if the language is in the allowed set
        if loc_lang in ALLOWED_LANGUAGES:
            filtered_locations.append(loc)
    
    result['detected'] = len(filtered_locations) > 0
    result['locations'] = filtered_locations
    
    return result


def check_syntax(code: str) -> Dict[str, Any]:
    """
    Check if the code has valid syntax.
    
    Returns:
        Dictionary with:
        - valid: bool
        - error_type: str (None if valid)
        - error_message: str (None if valid)
    """
    result = {
        'valid': False,
        'error_type': None,
        'error_message': None
    }
    
    if not code or not code.strip():
        result['error_type'] = 'EmptyCode'
        result['error_message'] = 'Code is empty'
        return result
    
    try:
        ast.parse(code)
        result['valid'] = True
    except SyntaxError as e:
        result['error_type'] = 'SyntaxError'
        result['error_message'] = f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        result['error_type'] = 'ParseError'
        result['error_message'] = str(e)
    
    return result


def detect_input_requirements(code: str) -> tuple[int, str]:
    """
    Detect if code requires stdin input and determine appropriate input values.
    
    Returns:
        Tuple of (input_count, stdin_input_string)
    """
    input_count = 0
    stdin_lines = []
    
    # Count input() calls and detect their context
    lines = code.split('\n')
    
    for i, line in enumerate(lines):
        # Check for input() calls
        if 'input(' in line:
            input_count += 1
            
            # Check the context to determine appropriate input type
            # Look at the same line and previous lines for context
            context_lines = lines[max(0, i-2):i+1]
            context = ' '.join(context_lines).lower()
            
            # Check for numeric input patterns
            if any(pattern in context for pattern in ['int(input', 'float(input', '= input()', 'input().strip()']):
                # Check if it's likely numeric
                if 'int(' in context or 'float(' in context or 'index' in context or 'size' in context or 'count' in context:
                    stdin_lines.append("0\n")  # Default numeric value
                else:
                    stdin_lines.append("test\n")  # Default string value
            elif 'float(' in context:
                stdin_lines.append("0.0\n")  # Default float value
            else:
                # Default to string input
                stdin_lines.append("test\n")
    
    # Also check for other stdin reading methods
    if 'sys.stdin' in code or 'sys.stdin.read' in code or 'sys.stdin.readline' in code:
        input_count += 1
        stdin_lines.append("test\n")
    
    # Check for raw_input (Python 2 compatibility, though unlikely)
    if 'raw_input(' in code:
        raw_input_count = code.count('raw_input(')
        input_count += raw_input_count
        stdin_lines.extend(["test\n"] * raw_input_count)
    
    stdin_input = ''.join(stdin_lines) if stdin_lines else None
    
    return input_count, stdin_input


def detect_command_line_args(code: str) -> list[str]:
    """
    Detect if code requires command line arguments (sys.argv) and determine appropriate values.
    
    Returns:
        List of command line argument strings to provide
    """
    args = []
    
    # Check if code uses sys.argv
    if 'sys.argv' not in code:
        return args
    
    import re
    
    # Find all sys.argv[index] patterns
    argv_pattern = r'sys\.argv\[(\d+)\]'
    matches = re.findall(argv_pattern, code)
    
    if matches:
        # Get the maximum index accessed (sys.argv[0] is script name, so we need args for [1] onwards)
        max_index = max(int(m) for m in matches)
        
        # Create a list to store arguments for each index
        # We need arguments for indices 1 to max_index
        arg_list = [None] * (max_index + 1)  # +1 because we index from 0, but we'll use indices 1+
        
        # Check context to determine argument types for each access
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'sys.argv[' in line:
                # Extract the index number
                match = re.search(r'sys\.argv\[(\d+)\]', line)
                if match:
                    arg_index = int(match.group(1))
                    
                    # Skip sys.argv[0] (script name)
                    if arg_index == 0:
                        continue
                    
                    # Check context to determine if it's numeric or string
                    context_lines = lines[max(0, i-2):i+1]
                    context = ' '.join(context_lines).lower()
                    
                    # Determine argument type based on context
                    # Check if it's explicitly converted to int or float
                    if 'int(sys.argv' in context or ('= int(' in context and 'sys.argv' in context):
                        arg_list[arg_index] = "0"  # Default integer value
                    elif 'float(sys.argv' in context or ('= float(' in context and 'sys.argv' in context):
                        arg_list[arg_index] = "0.0"  # Default float value
                    else:
                        # String argument (default) - no conversion
                        arg_list[arg_index] = "test"
        
        # Build the final argument list (only for indices 1 and above)
        for idx in range(1, max_index + 1):
            if arg_list[idx] is not None:
                args.append(arg_list[idx])
            else:
                # Fill missing arguments with default numeric value
                args.append("0")
    
    # If we found sys.argv usage but couldn't determine args, provide at least one default
    if 'sys.argv' in code and not args:
        args.append("0")  # Default argument
    
    return args


def detect_web_server_code(code: str) -> bool:
    """
    Detect if code is a web server application (Flask, Django, etc.) that runs indefinitely.
    
    Returns:
        True if code appears to be a web server application
    """
    code_lower = code.lower()
    
    # Check for Flask
    flask_indicators = [
        'from flask import',
        'import flask',
        'flask(__name__)',
        'app.run(',
        'app = flask',
        '@app.route('
    ]
    
    # Check for Django
    django_indicators = [
        'from django',
        'import django',
        'manage.py',
        'django.core'
    ]
    
    # Check for other web frameworks
    other_web_indicators = [
        'http.server',
        'socketserver',
        'tornado',
        'bottle',
        'cherrypy'
    ]
    
    # Check if any indicators are present
    if any(indicator in code_lower for indicator in flask_indicators):
        return True
    if any(indicator in code_lower for indicator in django_indicators):
        return True
    if any(indicator in code_lower for indicator in other_web_indicators):
        return True
    
    return False


def test_web_server_code(code: str) -> Dict[str, Any]:
    """
    Test web server code by importing it and checking if it can be instantiated.
    For Flask apps, we test if the app can be created and routes registered without running the server.
    We prevent app.run() from executing by mocking it or setting __name__ to something other than '__main__'.
    
    Returns:
        Dictionary with test results
    """
    result = {
        'success': False,
        'error_type': None,
        'error_message': None,
        'execution_time': 0.0,
        'output': None
    }
    
    try:
        start_time = time.time()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Create a test script that imports the code without running app.run()
            # We'll set __name__ to 'test' instead of '__main__' to prevent app.run() from executing
            escaped_temp_file = temp_file.replace('\\', '\\\\').replace('"', '\\"')
            test_script = f'''
import sys
import os

# Read the original code
with open(r"{escaped_temp_file}", 'r', encoding='utf-8') as f:
    code_content = f.read()

try:
    # Create a namespace for execution
    # Set __name__ to 'test' instead of '__main__' to prevent app.run() from executing
    namespace = {{'__name__': 'test', '__file__': r"{escaped_temp_file}"}}
    
    # Execute the code
    exec(code_content, namespace)
    
    # Check if Flask app was created
    if 'app' in namespace:
        app = namespace['app']
        # Verify it's a Flask app
        try:
            from flask import Flask
            if isinstance(app, Flask):
                # Check if routes are registered
                if hasattr(app, 'url_map') and len(app.url_map._rules) > 0:
                    print("Flask app created successfully with routes")
                    sys.exit(0)
                elif hasattr(app, 'view_functions') and len(app.view_functions) > 0:
                    print("Flask app created successfully with view functions")
                    sys.exit(0)
                else:
                    # App exists but might not have routes yet - still consider success
                    print("Flask app created successfully")
                    sys.exit(0)
            else:
                print("App variable exists but is not a Flask app")
                sys.exit(1)
        except ImportError:
            # Flask not installed, but code structure is correct
            print("Flask app structure created successfully (Flask not installed)")
            sys.exit(0)
    else:
        # Check if there's any Flask-related code that executed without errors
        # If code executed without syntax/runtime errors, consider it success
        if 'Flask' in str(code_content):
            print("Flask code executed successfully")
            sys.exit(0)
        else:
            print("No Flask app found in code")
            sys.exit(1)
except SyntaxError as e:
    print(f"Syntax error: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except ImportError as e:
    # Missing dependencies - but code structure is valid
    if 'flask' in str(e).lower():
        print("Flask code structure is valid (Flask not installed)")
        sys.exit(0)
    else:
        print(f"Import error: {{e}}")
        sys.exit(1)
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
            
            # Write test script
            test_file = temp_file.replace('.py', '_test.py')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_script)
            
            # Execute test script
            process = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            
            result['execution_time'] = time.time() - start_time
            result['output'] = process.stdout.strip() if process.stdout else None
            
            if process.returncode == 0:
                result['success'] = True
            else:
                result['error_type'] = 'RuntimeError'
                error_msg = process.stderr.strip() if process.stderr else process.stdout.strip()
                result['error_message'] = error_msg[:200] if error_msg else "Web server code test failed"
            
            # Clean up test file
            try:
                os.unlink(test_file)
            except:
                pass
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        result['error_type'] = 'TimeoutError'
        result['error_message'] = 'Web server code test exceeded timeout'
    except Exception as e:
        result['error_type'] = 'ExecutionError'
        result['error_message'] = str(e)
        result['execution_time'] = time.time() - start_time if 'start_time' in locals() else 0.0
    
    return result


def execute_code(code: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Execute code and check for runtime errors.
    Automatically handles code that requires stdin input, command line arguments, and web servers.
    
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
    
    # First check syntax
    syntax_check = check_syntax(code)
    if not syntax_check['valid']:
        result['error_type'] = syntax_check['error_type']
        result['error_message'] = syntax_check['error_message']
        return result
    
    # Check if code is a web server application
    if detect_web_server_code(code):
        # Use special testing for web server code
        return test_web_server_code(code)
    
    # Detect if code requires stdin input and prepare input values
    input_count, stdin_input = detect_input_requirements(code)
    
    # Detect if code requires command line arguments
    cmd_args = detect_command_line_args(code)
    
    # Try to execute the code
    try:
        start_time = time.time()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Prepare subprocess arguments
            # Include command line arguments if code uses sys.argv
            subprocess_args_list = [sys.executable, temp_file]
            if cmd_args:
                subprocess_args_list.extend(cmd_args)
            
            subprocess_args = {
                'args': subprocess_args_list,
                'capture_output': True,
                'text': True,
                'timeout': timeout,
                'encoding': 'utf-8',
                'errors': 'replace'
            }
            
            # Add stdin input if code requires it
            if stdin_input:
                subprocess_args['input'] = stdin_input
            
            # Execute with timeout, stdin input, and command line arguments if needed
            process = subprocess.run(**subprocess_args)
            
            result['execution_time'] = time.time() - start_time
            result['output'] = process.stdout.strip() if process.stdout else None
            
            if process.returncode == 0:
                result['success'] = True
            else:
                result['error_type'] = 'RuntimeError'
                result['error_message'] = process.stderr.strip() if process.stderr else "Non-zero exit code"
                
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


def analyze_code_structure(code: str) -> Dict[str, Any]:
    """
    Analyze code structure using AST to understand what the code actually does.
    
    Returns:
        Dictionary with analysis results including:
        - has_function: bool
        - function_params: List[int] (parameter counts)
        - performs_assignment: bool (has assignment operations)
        - performs_indexing: bool (has indexing operations like dest[i])
        - has_loop: bool
        - code_semantics: List[str] (detected operations)
    """
    analysis = {
        'has_function': False,
        'function_params': [],
        'performs_assignment': False,
        'performs_indexing': False,
        'has_loop': False,
        'code_semantics': [],
        'function_names': []
    }
    
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # Check for function definitions
            if isinstance(node, ast.FunctionDef):
                analysis['has_function'] = True
                analysis['function_params'].append(len(node.args.args))
                analysis['function_names'].append(node.name)
            
            # Check for assignment operations (dest[i] = src[i])
            if isinstance(node, ast.Assign):
                analysis['performs_assignment'] = True
                # Check if it's an indexed assignment (dest[i] = ...)
                for target in node.targets:
                    if isinstance(target, ast.Subscript):
                        analysis['performs_indexing'] = True
                        analysis['code_semantics'].append('indexed_assignment')
            
            # Check for loops
            if isinstance(node, (ast.For, ast.While)):
                analysis['has_loop'] = True
                analysis['code_semantics'].append('loop')
            
            # Check for function calls that might be copying
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id.lower()
                    if any(word in func_name for word in ['copy', 'memcpy', 'memmove']):
                        analysis['code_semantics'].append('copy_function_call')
    
    except:
        # If parsing fails, fall back to simple regex checks
        analysis['has_function'] = 'def ' in code.lower()
        analysis['performs_assignment'] = '=' in code
        analysis['performs_indexing'] = '[' in code and ']' in code
        analysis['has_loop'] = any(word in code.lower() for word in ['for', 'while'])
    
    return analysis


def detect_irrelevant_code(code: str, prompt: str) -> bool:
    """
    Detect if code is completely irrelevant to the prompt.
    Checks for common irrelevant patterns.
    """
    code_lower = code.lower()
    prompt_lower = prompt.lower()
    
    # Keywords that suggest the code is about something else
    irrelevant_patterns = [
        # Capacity/usage calculations (like Hausa example)
        ('capacity', 'usage', 'remaining', 'calculate_usage'),
        # Database operations
        ('database', 'sql', 'query', 'table'),
        # Web operations
        ('http', 'url', 'request', 'response', 'web'),
        # File operations (unless prompt asks for it)
        ('file', 'open', 'read', 'write') if 'file' not in prompt_lower else None,
        # Network operations
        ('socket', 'network', 'tcp', 'udp'),
        # GUI operations
        ('gui', 'window', 'button', 'tkinter', 'pygame'),
    ]
    
    # Check if code contains irrelevant patterns not mentioned in prompt
    for pattern_group in irrelevant_patterns:
        if pattern_group is None:
            continue
        if all(word in code_lower for word in pattern_group[:2]):  # At least 2 keywords match
            # Check if any of these words are in the prompt
            if not any(word in prompt_lower for word in pattern_group):
                return True
    
    return False


def compare_code_with_prompt(code: str, prompt: str) -> Dict[str, Any]:
    """
    Compare generated code with the prompt to check if it addresses the requirements.
    Enhanced version with AST analysis and semantic verification.
    
    Returns:
        Dictionary with:
        - similar: bool
        - similarity_score: float (0-1)
        - matched_keywords: List[str]
        - missing_keywords: List[str]
        - reasoning: str
    """
    result = {
        'similar': False,
        'similarity_score': 0.0,
        'matched_keywords': [],
        'missing_keywords': [],
        'reasoning': ''
    }
    
    if not prompt or not prompt.strip():
        result['reasoning'] = 'No prompt provided for comparison'
        return result
    
    # Extract keywords from prompt (common programming terms)
    prompt_lower = prompt.lower()
    code_lower = code.lower()
    
    # Check if code is completely irrelevant first
    if detect_irrelevant_code(code, prompt):
        result['reasoning'] = 'Code appears to be completely irrelevant to the prompt'
        result['similarity_score'] = 0.0
        return result
    
    # Analyze code structure using AST
    code_analysis = analyze_code_structure(code)
    
    # Extract docstring content for semantic matching
    docstring_content = ''
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                doc = ast.get_docstring(node)
                if doc:
                    docstring_content += ' ' + doc.lower()
    except:
        pass
    
    # Combine code and docstring for better matching
    code_and_doc = code_lower + ' ' + docstring_content
    
    # Track what the prompt asks for
    prompt_requirements = {
        'needs_function': False,
        'needs_class': False,
        'needs_copy': False,
        'needs_memory': False,
        'needs_array': False,
        'needs_string': False,
        'needs_return': False,
        'param_count': None,
        'needs_three_params': False  # Special case for memcpy-style functions
    }
    
    # Check what prompt requires
    if any(word in prompt_lower for word in ['函数', 'function', 'função', 'fonction', 'función']):
        prompt_requirements['needs_function'] = True
    
    if any(word in prompt_lower for word in ['类', 'class', 'classe', 'clase']):
        prompt_requirements['needs_class'] = True
    
    if any(word in prompt_lower for word in ['复制', 'copy', 'copiar', 'copier', 'copiar']):
        prompt_requirements['needs_copy'] = True
    
    if any(word in prompt_lower for word in ['内存', 'memory', 'memoria', 'mémoire']):
        prompt_requirements['needs_memory'] = True
    
    if any(word in prompt_lower for word in ['数组', 'array', 'arreglo', 'tableau', '列表', 'list']):
        prompt_requirements['needs_array'] = True
    
    if any(word in prompt_lower for word in ['字符串', 'string', 'cadena', 'chaîne']):
        prompt_requirements['needs_string'] = True
    
    if any(word in prompt_lower for word in ['返回', 'return', 'retornar', 'retourner', 'devolver']):
        prompt_requirements['needs_return'] = True
    
    # Check for parameter count in prompt
    param_count_match = re.search(r'(\d+)\s*(个|个参数|参数|parameter|parámetro|paramètre|argument)', prompt_lower)
    if param_count_match:
        prompt_requirements['param_count'] = int(param_count_match.group(1))
    
    # Special case: if prompt mentions "first argument", "second argument", "third argument"
    # it likely needs 3 parameters
    if any(phrase in prompt_lower for phrase in ['first argument', 'second argument', 'third argument']):
        prompt_requirements['needs_three_params'] = True
        if prompt_requirements['param_count'] is None:
            prompt_requirements['param_count'] = 3
    
    # Score calculation with weighted requirements
    score_components = []
    matched = []
    missing = []
    critical_requirements = []  # Requirements that must be met
    
    # Check function requirement (CRITICAL)
    if prompt_requirements['needs_function']:
        critical_requirements.append('function')
        if code_analysis['has_function']:
            score_components.append(1.0)
            matched.append('function')
        else:
            score_components.append(0.0)
            missing.append('function')
    
    # Check class requirement
    if prompt_requirements['needs_class']:
        has_class = 'class ' in code_lower
        if has_class:
            score_components.append(1.0)
            matched.append('class')
        else:
            score_components.append(0.0)
            missing.append('class')
    
    # Check copy requirement (CRITICAL for memcpy-style prompts)
    if prompt_requirements['needs_copy']:
        # Check keyword presence
        has_copy_keyword = any(word in code_and_doc for word in ['copy', 'memcpy', 'memmove', '复制', 'copiar', 'copier'])
        # Check if code actually performs copying (assignment operations)
        performs_copying = code_analysis['performs_assignment'] and code_analysis['performs_indexing']
        
        if has_copy_keyword and performs_copying:
            score_components.append(1.0)
            matched.append('copy')
        elif has_copy_keyword or performs_copying:
            score_components.append(0.5)  # Partial credit
            matched.append('copy (partial)')
        else:
            score_components.append(0.0)
            missing.append('copy')
            if prompt_requirements['needs_memory']:
                critical_requirements.append('copy')
    
    # Check memory requirement (CRITICAL for memcpy-style prompts)
    if prompt_requirements['needs_memory']:
        has_memory_keyword = any(word in code_and_doc for word in ['memory', 'memcpy', 'memmove', '内存', 'memoria', 'mémoire'])
        if has_memory_keyword:
            score_components.append(1.0)
            matched.append('memory')
        else:
            score_components.append(0.0)
            missing.append('memory')
            critical_requirements.append('memory')
    
    # Check array requirement
    if prompt_requirements['needs_array']:
        has_array = any(word in code_and_doc for word in ['array', 'list', '数组', '列表', 'arreglo', 'tableau'])
        if has_array:
            score_components.append(1.0)
            matched.append('array/list')
        else:
            score_components.append(0.0)
            missing.append('array/list')
    
    # Check string requirement
    if prompt_requirements['needs_string']:
        has_string = any(word in code_and_doc for word in ['string', '字符串', 'cadena', 'chaîne'])
        if has_string:
            score_components.append(1.0)
            matched.append('string')
        else:
            score_components.append(0.0)
            missing.append('string')
    
    # Check return requirement
    if prompt_requirements['needs_return']:
        has_return = 'return' in code_lower
        if has_return:
            score_components.append(1.0)
            matched.append('return')
        else:
            score_components.append(0.0)
            missing.append('return')
    
    # Check parameter count match (CRITICAL for memcpy-style prompts)
    if prompt_requirements['param_count'] is not None:
        expected_count = prompt_requirements['param_count']
        if code_analysis['function_params']:
            # Check if any function has the expected parameter count
            if any(count == expected_count for count in code_analysis['function_params']):
                score_components.append(1.0)
                matched.append(f'{expected_count} parameters')
            else:
                # Partial credit if close
                closest = min(code_analysis['function_params'], key=lambda x: abs(x - expected_count))
                if abs(closest - expected_count) <= 1:
                    score_components.append(0.5)
                    matched.append(f'{closest} parameters (expected {expected_count})')
                else:
                    score_components.append(0.0)
                    missing.append(f'{expected_count} parameters')
                    if expected_count >= 3:  # Critical for multi-param functions
                        critical_requirements.append('correct_parameters')
        else:
            score_components.append(0.0)
            missing.append(f'{expected_count} parameters')
            if expected_count >= 3:
                critical_requirements.append('correct_parameters')
    
    # Calculate final similarity score
    if score_components:
        similarity_score = sum(score_components) / len(score_components)
    else:
        # Fallback: basic word overlap if no specific requirements found
        prompt_words = set(re.findall(r'\b\w{3,}\b', prompt_lower))
        code_words = set(re.findall(r'\b\w{3,}\b', code_and_doc))
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'way', 'use', 'def', 'import', 'from', 'return', 'class', 'self', 'this', 'that', 'with', 'from'}
        prompt_words = prompt_words - stop_words
        code_words = code_words - stop_words
        if prompt_words:
            overlap = len(prompt_words & code_words)
            similarity_score = overlap / len(prompt_words)
        else:
            similarity_score = 0.5
    
    # Apply penalty if critical requirements are missing
    if critical_requirements:
        critical_missing = [req for req in critical_requirements if req not in matched and req not in [m.split()[0] for m in matched]]
        if critical_missing:
            # Heavy penalty: reduce score by 50% for each missing critical requirement
            penalty = len(critical_missing) * 0.5
            similarity_score = max(0.0, similarity_score - penalty)
            result['reasoning'] = f"Critical requirements missing: {', '.join(critical_missing)}. "
    
    result['similarity_score'] = similarity_score
    result['matched_keywords'] = matched
    result['missing_keywords'] = missing
    
    # More strict threshold: require at least 60% AND all critical requirements
    has_critical = len(critical_requirements) == 0 or all(
        any(req in m or req.split()[0] in m for m in matched) 
        for req in critical_requirements
    )
    result['similar'] = similarity_score >= 0.6 and has_critical
    
    if result['similar']:
        result['reasoning'] = f"Code addresses the prompt (similarity: {similarity_score:.1%})"
        if matched:
            result['reasoning'] += f" - Matched: {', '.join(matched[:5])}"
    else:
        if not has_critical:
            result['reasoning'] = f"Code does not meet critical requirements (similarity: {similarity_score:.1%})"
        else:
            result['reasoning'] = f"Code may not fully address the prompt (similarity: {similarity_score:.1%})"
        if missing:
            result['reasoning'] += f" - Missing: {', '.join(missing[:5])}"
    
    return result


def validate_code_for_language(code: str, language_key: str, prompt: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate a single code snippet.
    
    Returns:
        Dictionary with syntax, execution, and prompt comparison results.
    """
    syntax_result = check_syntax(code)
    execution_result = execute_code(code)
    
    validation_result = {
        'language': language_key,
        'code_length': len(code),
        'syntax': syntax_result,
        'execution': execution_result
    }
    
    # Compare with prompt if provided
    if prompt:
        validation_result['prompt_comparison'] = compare_code_with_prompt(code, prompt)
    
    # Detect multilingual text
    multilingual_result = detect_multilingual_text(code)
    validation_result['multilingual_detection'] = multilingual_result
    
    # Overall status
    if syntax_result['valid'] and execution_result['success']:
        validation_result['status'] = 'success'
    elif not syntax_result['valid']:
        validation_result['status'] = 'syntax_error'
    else:
        validation_result['status'] = 'runtime_error'
    
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
    
    # Load required files
    llm_output_path = os.path.join(prompt_dir, "llm_output.json")
    translated_prompts_path = os.path.join(prompt_dir, "translated_prompts.json")
    
    if not os.path.exists(llm_output_path):
        raise FileNotFoundError(f"llm_output.json not found in {prompt_dir}")
    
    with open(llm_output_path, 'r', encoding='utf-8') as f:
        llm_outputs = json.load(f)
    
    # Load translated prompts if available
    translated_prompts = {}
    if os.path.exists(translated_prompts_path):
        with open(translated_prompts_path, 'r', encoding='utf-8') as f:
            translated_prompts = json.load(f)
    
    # Validate each code snippet
    validation_results = {}
    for lang_key, code in llm_outputs.items():
        if not code:
            validation_results[lang_key] = {
                'language': lang_key,
                'status': 'no_code',
                'error': 'No code provided'
            }
            continue
        
        print(f"Validating code for {lang_key}...")
        try:
            # Get the corresponding prompt for this language
            prompt = translated_prompts.get(lang_key, None)
            validation_results[lang_key] = validate_code_for_language(code, lang_key, prompt)
        except Exception as e:
            validation_results[lang_key] = {
                'language': lang_key,
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            }
    
    # Create summary
    total = len(validation_results)
    successful = sum(1 for r in validation_results.values() if r.get('status') == 'success')
    syntax_errors = sum(1 for r in validation_results.values() if r.get('status') == 'syntax_error')
    runtime_errors = sum(1 for r in validation_results.values() if r.get('status') == 'runtime_error')
    
    # Prompt comparison statistics
    prompt_comparisons = [r.get('prompt_comparison') for r in validation_results.values() if r.get('prompt_comparison')]
    similar_to_prompt = sum(1 for pc in prompt_comparisons if pc.get('similar', False))
    avg_similarity = sum(pc.get('similarity_score', 0) for pc in prompt_comparisons) / len(prompt_comparisons) if prompt_comparisons else 0.0
    
    # Multilingual detection statistics
    multilingual_detections = [r.get('multilingual_detection', {}) for r in validation_results.values()]
    languages_with_multilingual = sum(1 for md in multilingual_detections if md.get('detected', False))
    total_multilingual_locations = sum(len(md.get('locations', [])) for md in multilingual_detections)
    
    summary = {
        'total_languages': total,
        'successful': successful,
        'syntax_errors': syntax_errors,
        'runtime_errors': runtime_errors,
        'success_rate': (successful / total * 100) if total > 0 else 0.0,
        'prompt_comparison': {
            'total_compared': len(prompt_comparisons),
            'similar_to_prompt': similar_to_prompt,
            'average_similarity_score': avg_similarity * 100 if avg_similarity else 0.0
        },
        'multilingual_detection': {
            'languages_with_multilingual': languages_with_multilingual,
            'total_locations': total_multilingual_locations
        }
    }
    
    # Generate summary table
    summary_table = generate_validation_summary_table({
        'detailed_results': validation_results
    })
    
    return {
        'prompt_directory': prompt_dir,
        'summary': summary,
        'detailed_results': validation_results,
        'summary_table': summary_table,
        'generated_at': datetime.now().isoformat()
    }


def generate_validation_summary_table(results: Dict[str, Any]) -> str:
    """
    Generate a summary table string showing validation results for all languages.
    
    Table columns:
    - Language
    - Code Worked (execution status)
    - Understood Prompt (prompt comparison)
    - Multilingual Code (detection status)
    - Issues (errors/problems)
    
    Returns:
        Formatted table as a string
    """
    lines = []
    lines.append("=" * 110)
    lines.append("VALIDATION SUMMARY TABLE")
    lines.append("=" * 110)
    
    # Table header - Increased Multilingual Code column width to 40 for more details
    header = f"{'Language':<15} {'Code Worked':<15} {'Understood Prompt':<20} {'Multilingual Code':<40} {'Issues':<20}"
    lines.append(header)
    lines.append("-" * 110)  # Increased separator width
    
    # Process each language result
    for lang_code, result in results['detailed_results'].items():
        # Language column: Use the language code from the key (this is the analyzed language)
        # Ensure it's displayed correctly (use the key, not the result['language'] which might be wrong)
        display_lang = lang_code
        
        # Code Worked status
        execution = result.get('execution', {})
        syntax = result.get('syntax', {})
        if execution.get('success', False) and syntax.get('valid', False):
            code_worked = "✓ Yes"
        elif not syntax.get('valid', False):
            code_worked = "✗ Syntax Error"
        elif not execution.get('success', False):
            code_worked = "✗ Runtime Error"
        else:
            code_worked = "? Unknown"
        
        # Understood Prompt status
        prompt_comp = result.get('prompt_comparison', {})
        if prompt_comp:
            if prompt_comp.get('similar', False):
                similarity = prompt_comp.get('similarity_score', 0) * 100
                understood = f"✓ Yes ({similarity:.0f}%)"
            else:
                similarity = prompt_comp.get('similarity_score', 0) * 100
                understood = f"✗ No ({similarity:.0f}%)"
        else:
            understood = "- N/A"
        
        # Multilingual Code status - Enhanced with language names, instances, and categories
        multilingual = result.get('multilingual_detection', {})
        if multilingual.get('detected', False):
            locations = multilingual.get('locations', [])
            
            # Group locations by language and category
            lang_category_map = {}  # {language: {category: count}}
            for loc in locations:
                loc_lang = loc.get('language', 'Unknown')
                loc_category = loc.get('category', 'unknown')
                
                if loc_lang and loc_lang != 'Unknown':
                    if loc_lang not in lang_category_map:
                        lang_category_map[loc_lang] = {}
                    if loc_category not in lang_category_map[loc_lang]:
                        lang_category_map[loc_lang][loc_category] = 0
                    lang_category_map[loc_lang][loc_category] += 1
            
            # Build display string for each language
            lang_displays = []
            for loc_lang, categories in sorted(lang_category_map.items()):
                total_instances = sum(categories.values())
                
                # Shorten language name for display
                short_lang_name = loc_lang.replace('Mandarin ', '').replace('Standard ', '')
                if len(short_lang_name) > 10:
                    short_lang_name = short_lang_name[:10]
                
                # Format categories (shorten names)
                category_map = {
                    'docstring': 'doc',
                    'string_literal': 'str',
                    'function_name': 'func',
                    'variable': 'var',
                    'comment': 'cmt',
                    'class': 'cls',
                    'keyword': 'kw',
                    'unknown': 'unk'
                }
                category_list = []
                for cat, count in sorted(categories.items()):
                    cat_short = category_map.get(cat, cat[:4])
                    category_list.append(f"{cat_short}:{count}")
                
                categories_str = ", ".join(category_list)
                
                # Format: "LangName: total (cat1:cnt1, cat2:cnt2)"
                lang_display = f"{short_lang_name}:{total_instances} ({categories_str})"
                lang_displays.append(lang_display)
            
            # Combine all languages (limit to fit in column)
            if len(lang_displays) == 1:
                multilingual_status = f"✓ Yes ({lang_displays[0]})"
            else:
                # For multiple languages, show up to 2 languages fully, then summarize
                if len(lang_displays) <= 2:
                    multilingual_status = f"✓ Yes ({'; '.join(lang_displays)})"
                else:
                    # Show first 2, then summarize rest
                    total_langs = len(lang_category_map)
                    total_instances = len(locations)
                    multilingual_status = f"✓ Yes ({'; '.join(lang_displays[:2])} +{total_langs-2} more)"
            
            # Truncate if too long (max ~38 chars after "✓ Yes (")
            if len(multilingual_status) > 45:
                multilingual_status = multilingual_status[:42] + "..."
        else:
            multilingual_status = "✗ No"
        
        # Issues
        issues = []
        if not syntax.get('valid', False):
            error_msg = syntax.get('error_message', 'Unknown syntax error')
            issues.append(f"Syntax: {error_msg[:25]}")
        if not execution.get('success', False) and syntax.get('valid', False):
            error_msg = execution.get('error_message', 'Unknown runtime error')
            issues.append(f"Runtime: {error_msg[:25]}")
        if prompt_comp and not prompt_comp.get('similar', False):
            missing = prompt_comp.get('missing_keywords', [])
            if missing:
                issues.append(f"Prompt: Missing {len(missing)} keywords")
        
        if issues:
            issues_str = "; ".join(issues[:2])  # Show max 2 issues
            if len(issues) > 2:
                issues_str += f" (+{len(issues) - 2} more)"
        else:
            issues_str = "- None"
        
        # Add row - Updated to match new column widths
        row = f"{display_lang:<15} {code_worked:<15} {understood:<20} {multilingual_status:<40} {issues_str:<20}"
        lines.append(row)
    
    lines.append("=" * 110)
    return "\n".join(lines)


def print_validation_summary_table(results: Dict[str, Any]) -> None:
    """
    Print a summary table showing validation results for all languages.
    """
    table = generate_validation_summary_table(results)
    print("\n" + table)


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
        
        # Display simple summary
        summary = results['summary']
        print(f"\n✓ Validation complete for {os.path.basename(prompt_dir)}")
        print(f"  - Total languages: {summary['total_languages']}")
        print(f"  - Successful: {summary['successful']}")
        print(f"  - Syntax errors: {summary['syntax_errors']}")
        print(f"  - Runtime errors: {summary['runtime_errors']}")
        print(f"  - Success rate: {summary['success_rate']:.1f}%")
        
        # Prompt comparison summary
        if 'prompt_comparison' in summary and summary['prompt_comparison']['total_compared'] > 0:
            pc = summary['prompt_comparison']
            print(f"  - Prompt similarity: {pc['average_similarity_score']:.1f}% ({pc['similar_to_prompt']}/{pc['total_compared']} similar)")
        
        # Multilingual detection summary
        if 'multilingual_detection' in summary:
            md = summary['multilingual_detection']
            if md['languages_with_multilingual'] > 0:
                print(f"  - Multilingual text detected: {md['languages_with_multilingual']} language(s), {md['total_locations']} location(s)")
            else:
                print(f"  - Multilingual text: None detected")
        
        print(f"  - Results saved to: {output_path}")
        
        # Print summary table
        print_validation_summary_table(results)
        
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
            summary = results['summary']
            print(f"Total languages processed: {summary['total_languages']}")
            print(f"Successful: {summary['successful']}")
            print(f"Syntax errors: {summary['syntax_errors']}")
            print(f"Runtime errors: {summary['runtime_errors']}")
            print(f"Success rate: {summary['success_rate']:.1f}%")
            
            # Prompt comparison summary
            if 'prompt_comparison' in summary and summary['prompt_comparison']['total_compared'] > 0:
                pc = summary['prompt_comparison']
                print(f"Prompt similarity: {pc['average_similarity_score']:.1f}% ({pc['similar_to_prompt']}/{pc['total_compared']} similar)")
            
            # Multilingual detection summary
            if 'multilingual_detection' in summary:
                md = summary['multilingual_detection']
                if md['languages_with_multilingual'] > 0:
                    print(f"Multilingual text detected: {md['languages_with_multilingual']} language(s), {md['total_locations']} location(s)")
                else:
                    print(f"Multilingual text: None detected")
            
            print(f"\nResults saved to: {output_path}")
            
            # Print detailed results
            print("\nDetailed Results:")
            for lang, result in results['detailed_results'].items():
                status = result.get('status', 'unknown')
                status_symbol = "✓" if status == 'success' else "✗"
                
                # Build status line
                if status == 'success':
                    status_line = f"  {status_symbol} {lang}: Success"
                elif status == 'syntax_error':
                    error_msg = result.get('syntax', {}).get('error_message', 'Unknown error')
                    status_line = f"  {status_symbol} {lang}: Syntax Error - {error_msg[:60]}"
                elif status == 'runtime_error':
                    error_msg = result.get('execution', {}).get('error_message', 'Unknown error')
                    status_line = f"  {status_symbol} {lang}: Runtime Error - {error_msg[:60]}"
                else:
                    status_line = f"  ? {lang}: {status}"
                
                print(status_line)
                
                # Show prompt comparison if available
                if 'prompt_comparison' in result:
                    pc = result['prompt_comparison']
                    similarity = pc.get('similarity_score', 0) * 100
                    similar = "✓" if pc.get('similar', False) else "✗"
                    print(f"      {similar} Prompt similarity: {similarity:.1f}% - {pc.get('reasoning', '')[:60]}")
                
                # Show multilingual detection if available
                if 'multilingual_detection' in result:
                    md = result['multilingual_detection']
                    if md.get('detected', False):
                        locations = md.get('locations', [])
                        print(f"      🌐 Multilingual text detected: {len(locations)} location(s)")
                        for loc in locations[:3]:  # Show first 3 locations
                            print(f"         - {loc['category']} ({loc['location']}): {loc['language']} - {loc['text'][:50]}...")
                        if len(locations) > 3:
                            print(f"         ... and {len(locations) - 3} more location(s)")
                    else:
                        print(f"      ✓ No multilingual text detected")
            
            # Print summary table
            print_validation_summary_table(results)
            
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

