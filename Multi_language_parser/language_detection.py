import json
import re
from collections import defaultdict
import matplotlib.pyplot as plt
import os

# Try to import langdetect for Latin-based language detection
try:
    from langdetect import detect, DetectorFactory, LangDetectException
    LANGDETECT_AVAILABLE = True
    # Set seed for consistent results
    DetectorFactory.seed = 0
except ImportError:
    LANGDETECT_AVAILABLE = False

# Try to import pycld2 for Hausa detection (langdetect doesn't support Hausa)
try:
    import pycld2 as cld2
    CLD2_AVAILABLE = True
except ImportError:
    CLD2_AVAILABLE = False

# Unicode script ranges
UNICODE_SCRIPTS = [
    (re.compile(r'[\u4E00-\u9FFF]'), 'CJK Unified Ideographs'),
    (re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]'), 'Japanese (Hiragana/Katakana/Kanji)'),
    (re.compile(r'[\uAC00-\uD7AF]'), 'Hangul (Korean)'),
    (re.compile(r'[\u0600-\u06FF]'), 'Arabic'),
    (re.compile(r'[\u0590-\u05FF]'), 'Hebrew'),
    (re.compile(r'[\u0900-\u097F]'), 'Devanagari (Hindi, etc.)'),
    (re.compile(r'[\u0B80-\u0BFF]'), 'Tamil'),
    (re.compile(r'[\u0C00-\u0C7F]'), 'Telugu'),
    (re.compile(r'[\u0E00-\u0E7F]'), 'Thai'),
    (re.compile(r'[\u0400-\u04FF]'), 'Cyrillic'),
    (re.compile(r'[\u0370-\u03FF]'), 'Greek and Coptic'),
    (re.compile(r'[\u0980-\u09FF]'), 'Bengali'),
    (re.compile(r'[\u0A80-\u0AFF]'), 'Gujarati'),
]

# Common English programming terms that should NEVER be classified as non-English
COMMON_PROGRAMMING_TERMS = {
    # Memory/pointer operations
    'memcpy', 'memmove', 'memset', 'memcmp', 'malloc', 'free', 'dest', 'src',
    'destination', 'source', 'memory', 'mem', 'ptr', 'pointer', 'address',
    'current_dest', 'current_src',
    # Common variable names
    'min', 'max', 'sum', 'count', 'len', 'str', 'int', 'float', 'bool',
    'list', 'dict', 'set', 'tuple', 'array', 'arr', 'obj', 'val', 'var',
    'bytes', 'byte', 'bytearray', 'buffer', 'buff',
    # Control flow
    'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally',
    'def', 'class', 'import', 'from', 'as', 'return', 'pass', 'break', 'continue',
    # Data types and functions
    'string', 'integer', 'boolean', 'function', 'method', 'property',
    # Common identifiers
    'data', 'info', 'config', 'settings', 'options', 'params', 'args', 'kwargs',
    'file', 'path', 'dir', 'name', 'id', 'key', 'value', 'item', 'items',
    'user', 'admin', 'test', 'error', 'success', 'result', 'results',
    # HTML/web
    'html', 'http', 'https', 'url', 'uri', 'form', 'input', 'button', 'label',
    # System/library
    'sys', 'os', 'json', 'xml', 'csv', 'db', 'sql',
    'libc', 'linux', 'windows', 'macos', 'mac', 'unix',
    # Common English phrases in code comments
    'use', 'for', 'with', 'from', 'to', 'the', 'a', 'an',
    # C types and ctypes
    'c_size_t', 'c_void_p', 'restype', 'argtypes', 'cdll',
    # Python builtins and exceptions
    'hasattr', 'getattr', 'setattr', 'isinstance', 'typeerror', 'valueerror',
    'keyerror', 'indexerror', 'attributeerror', 'runtimeerror',
    # Python magic methods
    '__getitem__', '__setitem__', '__delitem__', '__len__', '__str__', '__repr__',
    '__init__', '__new__', '__call__', '__enter__', '__exit__',
    # Additional common words
    'num', 'number', 'numbers', 'size', 'length', 'width', 'height',
    'index', 'idx', 'pos', 'position', 'offset', 'limit', 'offset',
    'type', 'types', 'kind', 'mode', 'status', 'state', 'flag', 'flags',
    'time', 'date', 'timestamp', 'now', 'today', 'yesterday',
    'get', 'set', 'add', 'remove', 'update', 'delete', 'create', 'read', 'write',
    'save', 'load', 'find', 'search', 'filter', 'map', 'reduce', 'sort',
    'start', 'stop', 'begin', 'end', 'init', 'initialize', 'reset', 'clear',
    'copy', 'clone', 'move', 'rename', 'exists', 'check', 'validate',
    'true', 'false', 'none', 'null', 'undefined', 'empty', 'full',
    'new', 'old', 'first', 'last', 'next', 'prev', 'previous',
    'total', 'all', 'each', 'every', 'some', 'any', 'none',
    'row', 'rows', 'column', 'columns', 'cell', 'cells', 'table', 'tables',
    'record', 'records', 'entry', 'entries', 'field', 'fields',
    'page', 'pages', 'page_num', 'page_size', 'pagination',
    'request', 'requests', 'response', 'responses', 'header', 'headers',
    'body', 'content', 'text', 'texts', 'message', 'messages',
    'email', 'emails', 'mail', 'mails', 'subject', 'body',
    'token', 'tokens', 'auth', 'authorization', 'permission', 'permissions',
    'session', 'sessions', 'cookie', 'cookies', 'cache', 'cached',
    'log', 'logs', 'logger', 'logging', 'debug', 'info', 'warn', 'warning', 'error',
    'max_memory', 'max_size', 'max_length', 'max_count', 'max_value',
    'min_memory', 'min_size', 'min_length', 'min_count', 'min_value',
    # Usage/capacity related
    'usage', 'capacity', 'used', 'remaining', 'initial', 'additional',
    'calculate', 'current', 'values', 'value',
    # Function/variable naming patterns
    'memcpy_func', 'func', 'callback', 'handler',
}

def _is_programming_term(text):
    """Check if text is a common English programming term."""
    text_lower = text.strip().lower()
    
    # Skip pure numbers (they're not language-specific)
    if text_lower.isdigit():
        return True
    
    # Exact match
    if text_lower in COMMON_PROGRAMMING_TERMS:
        return True
    
    # Check for dot-separated library names (e.g., "libc.so.6", "msvcrt.dll")
    if '.' in text_lower:
        parts = text_lower.split('.')
        # If first part is a library name and rest are extensions/versions
        if parts[0] in ('libc', 'msvcrt', 'dylib') or parts[0].startswith('lib'):
            return True
    
    # Check for common English programming comment patterns
    # Patterns like "For X, use: ..." or "Use X from Y" are English
    english_comment_patterns = [
        r'^for\s+\w+,\s*use:',
        r'^use\s+\w+',
        r'^define\s+the',
        r'^perform\s+the',
        r'^return\s+the',
        r'^check\s+if',
        r'^assuming\s+',
        r'^this\s+is\s+a',
        r'^here\s+we\s+',
        r'^we\'ll\s+use',
        r'ctypes\.cdll',
        r'libc\s*=\s*ctypes',
        r'^for\s+macos',
        r'^for\s+windows',
        r'^for\s+linux',
    ]
    import re
    for pattern in english_comment_patterns:
        if re.match(pattern, text_lower, re.IGNORECASE):
            return True
    
    # Check for Indonesian comment patterns that might be mixed with English
    # If text starts with Indonesian words but contains English, don't exclude it
    # (Let langdetect handle it properly)
    indonesian_comment_starters = ['muat', 'ambil', 'panggil', 'kembalikan', 'simpan', 'baca']
    if any(text_lower.startswith(starter + ' ') for starter in indonesian_comment_starters):
        # Don't exclude - let langdetect detect it as Indonesian
        pass
    
    # Check for space-separated phrases where all words are programming terms
    # (e.g., "Initial values", "Current state", "Set value")
    if ' ' in text_lower:
        words = text_lower.split()
        # If all words are programming terms, it's a programming term
        if all(word in COMMON_PROGRAMMING_TERMS or word.isdigit() or len(word) <= 2 for word in words):
            return True
        # Common English programming phrases
        common_phrases = {
            'initial values', 'initial value', 'current state', 'set value', 'get value',
            'return value', 'default value', 'new value', 'old value', 'first value',
            'last value', 'next value', 'previous value', 'final value', 'max value',
            'min value', 'total value', 'all values', 'each value', 'some value',
            'any value', 'no value', 'null value', 'empty value', 'full value',
            'initial state', 'current value', 'set state', 'get state', 'return state',
            'default state', 'new state', 'old state', 'first state', 'last state',
            'next state', 'previous state', 'final state', 'max state', 'min state',
            'total state', 'all states', 'each state', 'some state', 'any state',
            'no state', 'null state', 'empty state', 'full state',
        }
        if text_lower in common_phrases:
            return True
    
    # Check for underscore-separated compound terms (e.g., "max_memory", "user_name")
    if '_' in text_lower:
        parts = text_lower.split('_')
        # If all parts are programming terms or numbers, it's a programming term
        if all(part in COMMON_PROGRAMMING_TERMS or part.isdigit() or len(part) <= 2 for part in parts):
            return True
        # If first part is a common prefix
        if parts[0] in COMMON_PROGRAMMING_TERMS:
            return True
        # Common compound patterns
        common_compound_patterns = {
            'current_dest', 'current_src', 'memcpy_func', 'max_memory', 'min_memory',
            'additional_usage', 'calculate_usage', 'remaining_after', 'initial_capacity',
            'used_capacity', 'remaining_capacity', 'total_used',
        }
        if text_lower in common_compound_patterns:
            return True
    
    # Pattern matching: word + number (e.g., "user1", "test123")
    import re
    programming_word_pattern = r'^(memcpy|memmove|memset|memcmp|malloc|free|dest|src|destination|source|memory|min|max|sum|count|len|str|int|float|bool|list|dict|set|tuple|array|arr|obj|val|var|bytes|byte|data|info|config|file|path|dir|name|id|key|value|user|admin|test|error|success|result|num|number|size|length|index|pos|type|time|date|get|set|add|remove|update|delete|create|read|write|save|load|find|search|filter|map|sort|start|stop|begin|end|init|copy|clone|move|row|column|cell|table|record|entry|field|page|request|response|header|body|content|text|message|email|token|auth|session|cookie|log|debug|restype|libc|current|usage|capacity|remaining|additional|calculate)[0-9]*$'
    if re.match(programming_word_pattern, text_lower):
        return True
    
    # Check for Python magic methods (double underscore patterns)
    if text_lower.startswith('__') and text_lower.endswith('__'):
        return True
    
    # Check for C type patterns (c_*, libc*, etc.)
    if text_lower.startswith('c_') or text_lower.startswith('libc'):
        return True
    
    # Very short identifiers (1-3 chars) are likely programming terms
    if len(text_lower) <= 3 and text_lower.isalpha():
        return True
    
    return False

# Helper to classify a string
def classify_string(s):
    total = len(s)
    if total == 0:
        return {'script': 'English/ASCII', 'confidence': 1.0}
    
    # Check if it's a common programming term first
    if _is_programming_term(s):
        return {'script': 'English/ASCII', 'confidence': 1.0}
    
    script_counts = defaultdict(int)
    for c in s:
        found = False
        for regex, script in UNICODE_SCRIPTS:
            if regex.match(c):
                script_counts[script] += 1
                found = True
                break
        if not found and ord(c) > 127:
            script_counts['Other Non-English'] += 1
    if not script_counts:
        # No Unicode script found - could be English/ASCII or Latin-based language
        # First check for Hausa using CLD2 (langdetect doesn't support Hausa)
        if CLD2_AVAILABLE and len(s.strip()) >= 10:  # CLD2 needs sufficient text
            try:
                is_reliable, text_bytes, details = cld2.detect(s)
                if is_reliable and details:
                    lang_name, lang_code, percent, score = details[0]
                    if lang_code.lower() == 'ha':  # Hausa
                        return {'script': 'Hausa (Latin)', 'confidence': min(percent / 100.0, 0.9)}
            except Exception:
                pass
        
        # Use langdetect to check if it's a non-English Latin language
        if LANGDETECT_AVAILABLE and len(s.strip()) >= 3:  # langdetect needs at least 3 chars
            try:
                detected_lang = detect(s)
                # Map language codes to script categories
                if detected_lang != 'en':
                    # Latin-based non-English languages
                    latin_languages = {
                        'es': 'Spanish (Latin)',
                        'pt': 'Portuguese (Latin)',
                        'fr': 'French (Latin)',
                        'it': 'Italian (Latin)',
                        'de': 'German (Latin)',
                        'tr': 'Turkish (Latin)',
                        'pl': 'Polish (Latin)',
                        'nl': 'Dutch (Latin)',
                        'ro': 'Romanian (Latin)',
                        'hu': 'Hungarian (Latin)',
                        'cs': 'Czech (Latin)',
                        'sv': 'Swedish (Latin)',
                        'da': 'Danish (Latin)',
                        'fi': 'Finnish (Latin)',
                        'no': 'Norwegian (Latin)',
                        'vi': 'Vietnamese (Latin)',
                        'id': 'Indonesian (Latin)',
                        'ms': 'Malay (Latin)',
                        'te': 'Telugu (Latin)',  # For Telugu written in Latin script (rare but possible)
                    }
                    script_name = latin_languages.get(detected_lang, 'Other Non-English (Latin)')
                    return {'script': script_name, 'confidence': 0.8}  # Lower confidence for langdetect
            except (LangDetectException, Exception):
                # If langdetect fails, default to English/ASCII
                pass
        return {'script': 'English/ASCII', 'confidence': 1.0}
    # Find the dominant script
    dominant_script = max(script_counts, key=script_counts.get)
    confidence = script_counts[dominant_script] / total
    
    # If Unicode detection found "Other Non-English", try to identify the specific language using langdetect
    if dominant_script == 'Other Non-English' and len(s.strip()) >= 3:
        # First check for Hausa using CLD2 (langdetect doesn't support Hausa)
        if CLD2_AVAILABLE and len(s.strip()) >= 10:
            try:
                is_reliable, text_bytes, details = cld2.detect(s)
                if is_reliable and details:
                    lang_name, lang_code, percent, score = details[0]
                    if lang_code.lower() == 'ha':  # Hausa
                        cld2_confidence = min(percent / 100.0, 0.9)
                        return {'script': 'Hausa (Latin)', 'confidence': round((confidence + cld2_confidence) / 2, 2)}
            except Exception:
                pass
        
        # Use langdetect to identify the specific language
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(s)
                if detected_lang != 'en':
                    # Latin-based non-English languages
                    latin_languages = {
                        'es': 'Spanish (Latin)',
                        'pt': 'Portuguese (Latin)',
                        'fr': 'French (Latin)',
                        'it': 'Italian (Latin)',
                        'de': 'German (Latin)',
                        'tr': 'Turkish (Latin)',
                        'pl': 'Polish (Latin)',
                        'nl': 'Dutch (Latin)',
                        'ro': 'Romanian (Latin)',
                        'hu': 'Hungarian (Latin)',
                        'cs': 'Czech (Latin)',
                        'sv': 'Swedish (Latin)',
                        'da': 'Danish (Latin)',
                        'fi': 'Finnish (Latin)',
                        'no': 'Norwegian (Latin)',
                        'vi': 'Vietnamese (Latin)',
                        'id': 'Indonesian (Latin)',
                        'ms': 'Malay (Latin)',
                        'te': 'Telugu (Latin)',  # For Telugu written in Latin script (rare but possible)
                    }
                    script_name = latin_languages.get(detected_lang, 'Other Non-English (Latin)')
                    # Use average confidence between Unicode and langdetect
                    return {'script': script_name, 'confidence': round((confidence + 0.8) / 2, 2)}
            except (LangDetectException, Exception):
                # If langdetect fails, keep "Other Non-English"
                pass
    
    # If Unicode detection found English/ASCII but text is long enough, double-check with CLD2 (for Hausa) and langdetect
    if dominant_script == 'English/ASCII' and len(s.strip()) >= 5:
        # First check for Hausa using CLD2 (langdetect doesn't support Hausa)
        if CLD2_AVAILABLE and len(s.strip()) >= 10:
            try:
                is_reliable, text_bytes, details = cld2.detect(s)
                if is_reliable and details:
                    lang_name, lang_code, percent, score = details[0]
                    if lang_code.lower() == 'ha':  # Hausa
                        cld2_confidence = min(percent / 100.0, 0.9)
                        return {'script': 'Hausa (Latin)', 'confidence': round((confidence + cld2_confidence) / 2, 2)}
            except Exception:
                pass
        
        # Use langdetect to check if it's a non-English Latin language
        if LANGDETECT_AVAILABLE:
            try:
                detected_lang = detect(s)
                if detected_lang != 'en':
                    # Latin-based non-English languages
                    latin_languages = {
                        'es': 'Spanish (Latin)',
                        'pt': 'Portuguese (Latin)',
                        'fr': 'French (Latin)',
                        'it': 'Italian (Latin)',
                        'de': 'German (Latin)',
                        'tr': 'Turkish (Latin)',
                        'pl': 'Polish (Latin)',
                        'nl': 'Dutch (Latin)',
                        'ro': 'Romanian (Latin)',
                        'hu': 'Hungarian (Latin)',
                        'cs': 'Czech (Latin)',
                        'sv': 'Swedish (Latin)',
                        'da': 'Danish (Latin)',
                        'fi': 'Finnish (Latin)',
                        'no': 'Norwegian (Latin)',
                        'vi': 'Vietnamese (Latin)',
                        'id': 'Indonesian (Latin)',
                        'ms': 'Malay (Latin)',
                        'te': 'Telugu (Latin)',  # For Telugu written in Latin script (rare but possible)
                    }
                    script_name = latin_languages.get(detected_lang, 'Other Non-English (Latin)')
                    # Use average confidence between Unicode and langdetect
                    return {'script': script_name, 'confidence': round((confidence + 0.8) / 2, 2)}
            except (LangDetectException, Exception):
                # If langdetect fails, use Unicode result
                pass
    
    return {'script': dominant_script, 'confidence': round(confidence, 2)}

def create_pie_chart(data, title, output_path):
    """Create a pie chart from the given data and save it."""
    # Extract labels and sizes
    labels = ['English/ASCII', 'Non-English']
    sizes = [data['english_ascii']['percentage'], data['non_english']['percentage']]
    
    # Create figure and axis
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title(title)
    
    # Save the plot
    plt.savefig(output_path)
    plt.close()

def main():
    with open('repo_analysis_results.json', encoding='utf-8') as f:
        data = json.load(f)
    elements = data['repository_elements']
    results = {}
    english_count = 0
    non_english_count = 0
    total_count = 0
    
    # Process elements
    for key, items in elements.items():
        results[key] = []
        for item in items:
            info = classify_string(item)
            results[key].append({'value': item, 'script': info['script'], 'confidence': info['confidence']})
            total_count += 1
            if info['script'] == 'English/ASCII':
                english_count += 1
            else:
                non_english_count += 1

    # Create structured output
    output = {
        "overall_statistics": {
            "total_elements": total_count,
            "english_ascii": {
                "count": english_count,
                "percentage": round(english_count/total_count*100, 2)
            },
            "non_english": {
                "count": non_english_count,
                "percentage": round(non_english_count/total_count*100, 2)
            }
        },
        "english_ascii_parts": {},
        "non_english_parts": {}
    }

    # Group English and non-English parts
    for key, items in results.items():
        english_items = [entry for entry in items if entry['script'] == 'English/ASCII']
        non_english_items = [entry for entry in items if entry['script'] != 'English/ASCII']
        
        if english_items:
            output["english_ascii_parts"][key] = {
                "instances": len(english_items),
                "confidence_score": round(sum(entry['confidence'] for entry in english_items) / len(english_items), 2),
                "parsed_instances": [entry['value'] for entry in english_items],
                "total_count": len(english_items)
            }
        
        if non_english_items:
            output["non_english_parts"][key] = {
                "instances": len(non_english_items),
                "confidence_score": round(sum(entry['confidence'] for entry in non_english_items) / len(non_english_items), 2),
                "parsed_instances": [f"{entry['value']}: {entry['script']} (confidence: {entry['confidence']})" 
                                  for entry in non_english_items],
                "total_count": len(non_english_items)
            }

    # Create output directory for charts if it doesn't exist
    os.makedirs('language_charts', exist_ok=True)

    # Create overall pie chart
    create_pie_chart(
        output['overall_statistics'],
        'Overall Language Distribution',
        'language_charts/overall_distribution.png'
    )

    # Create individual pie charts for each file
    for key in results.keys():
        if key in output['english_ascii_parts'] or key in output['non_english_parts']:
            english_count = output['english_ascii_parts'].get(key, {}).get('total_count', 0)
            non_english_count = output['non_english_parts'].get(key, {}).get('total_count', 0)
            total = english_count + non_english_count
            
            if total > 0:
                file_stats = {
                    'english_ascii': {
                        'percentage': round(english_count/total*100, 2)
                    },
                    'non_english': {
                        'percentage': round(non_english_count/total*100, 2)
                    }
                }
                create_pie_chart(
                    file_stats,
                    f'Language Distribution - {key}',
                    f'language_charts/{key}_distribution.png'
                )

    # Save to file
    with open('language_classification_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Print the results in a readable format
    print("\nLanguage Detection Results Summary:")
    print("=" * 80)
    print(f"Total Elements: {output['overall_statistics']['total_elements']}")
    print(f"English/ASCII Content: {output['overall_statistics']['english_ascii']['percentage']}%")
    print(f"Non-English Content: {output['overall_statistics']['non_english']['percentage']}%")
    print("=" * 80)
    print("\nCharts have been generated in the 'language_charts' directory")

if __name__ == '__main__':
    main()
