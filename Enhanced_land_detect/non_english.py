import os
import sys
import json
from collections import defaultdict
from typing import Dict, Any, List, Optional

import matplotlib.pyplot as plt


def ensure_mlp_on_path(project_root: str) -> str:
    mlp_dir = os.path.join(project_root, "Multi_language_parser")
    if mlp_dir not in sys.path:
        sys.path.insert(0, mlp_dir)
    return mlp_dir


def classify_text(text: str) -> str:
    """Return script label using Multi_language_parser.language_detection.classify_string.
    
    Enhanced to detect non-English languages that use Latin alphabet (Portuguese, Spanish, etc.)
    by checking word components in identifiers and using library-based detection (langdetect).
    """
    # Skip very short text (likely false positives)
    if len(text.strip()) < 2:
        return "English/ASCII"
    
    # Whitelist: Common English programming terms that should NEVER be classified as non-English
    text_lower = text.strip().lower()
    common_english_programming_terms = {
        # User/auth related
        'user', 'users', 'username', 'usernames', 'user_data', 'user_name',
        'password', 'passwords', 'pass', 'pass1', 'pass2', 'pass123', 'password123',
        'admin', 'admin1', 'admin2', 'admins', 'administrator',
        'login', 'logout', 'log', 'logs', 'logged', 'logging',
        'auth', 'authentication', 'authorize', 'authorization',
        'session', 'sessions', 'cookie', 'cookies',
        # Data related
        'data', 'database', 'db', 'databases', 'data_base',
        'table', 'tables', 'row', 'rows', 'column', 'columns',
        'record', 'records', 'entry', 'entries',
        # Web/HTML related
        'html', 'html_template', 'html_page', 'html_content', 'html_string',
        'http', 'https', 'url', 'urls', 'uri', 'uris',
        'form', 'forms', 'input', 'inputs', 'button', 'buttons',
        'label', 'labels', 'text', 'texts', 'textarea', 'textareas',
        'submit', 'submits', 'reset', 'resets', 'required',
        'method', 'methods', 'action', 'actions', 'type', 'types',
        'name', 'names', 'id', 'ids', 'key', 'keys', 'value', 'values',
        'class', 'classes', 'style', 'styles', 'title', 'titles',
        'head', 'heads', 'body', 'bodies', 'div', 'divs', 'span', 'spans',
        'p', 'paragraph', 'paragraphs', 'a', 'link', 'links', 'href',
        'img', 'image', 'images', 'src', 'alt',
        'script', 'scripts', 'meta', 'metas', 'doctype',
        # Page/template related
        'page', 'pages', 'template', 'templates', 'view', 'views',
        'dashboard', 'dashboards', 'home', 'homes', 'index', 'indexes',
        'main', 'error', 'errors', 'success', 'message', 'messages',
        'info', 'information', 'content', 'contents',
        # File/system related
        'file', 'files', 'dir', 'directory', 'directories', 'path', 'paths',
        'code', 'codes', 'function', 'functions', 'method', 'methods',
        'class', 'classes', 'object', 'objects', 'instance', 'instances',
        # Data types
        'string', 'strings', 'str', 'int', 'integer', 'integers',
        'float', 'floats', 'bool', 'boolean', 'booleans',
        'list', 'lists', 'dict', 'dictionary', 'dictionaries',
        'set', 'sets', 'tuple', 'tuples',
        # Control flow
        'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally',
        'return', 'def', 'class', 'import', 'from', 'as',
        'true', 'false', 'none', 'null', 'undefined',
        # Common patterns
        'get', 'set', 'add', 'remove', 'update', 'delete', 'clear',
        'copy', 'clone', 'create', 'read', 'write', 'save', 'load',
        'find', 'search', 'filter', 'map', 'reduce', 'sort',
        'min', 'max', 'sum', 'count', 'length', 'len',
        'start', 'stop', 'begin', 'end', 'init', 'initialize',
        'test', 'tests', 'test1', 'test2', 'test_data',
        'config', 'configuration', 'settings', 'options',
        'request', 'requests', 'response', 'responses',
        'email', 'emails', 'mail', 'mails',
        # Additional common English words
        'render', 'redirect', 'secret', 'public', 'private', 'secure',
        'jane', 'john', 'smith', 'doe', 'jane_smith', 'john_doe',
        'invalid', 'valid', 'validate', 'validation',
    }
    
    # Handle URL paths (e.g., "/login", "/info")
    if text_lower.startswith('/'):
        # Extract the path part (remove leading slash)
        path_part = text_lower[1:].split('/')[0].split('?')[0]
        # Common URL path terms
        common_paths = {'login', 'logout', 'info', 'home', 'index', 'main', 'dashboard', 
                       'page', 'pages', 'form', 'forms', 'api', 'admin', 'user', 'users',
                       'profile', 'settings', 'config', 'error', 'success', 'about', 'contact'}
        if path_part in common_paths:
            return "English/ASCII"
    
    # Check if it's a common English programming term (exact match)
    if text_lower in common_english_programming_terms:
        return "English/ASCII"
    
    # Check if it's a pattern like "user1", "pass123" (word + number)
    import re
    if re.match(r'^(user|pass|admin|test|data|info|name|id|key|val|email|login|page|form|button|label|input|html|http|url|file|dir|path|code|func|method|class|obj|str|int|float|bool|list|dict|set|tuple)[0-9]*$', text_lower):
        return "English/ASCII"
    
    # Check for compound words without underscores (e.g., "securepass" = "secure" + "pass")
    # Common English word prefixes that form compound words
    english_word_prefixes = {
        'secure', 'public', 'private', 'admin', 'user', 'pass', 'login', 'logout',
        'data', 'info', 'html', 'http', 'url', 'form', 'input', 'button', 'label',
        'text', 'page', 'template', 'file', 'dir', 'path', 'code', 'func', 'method',
        'class', 'obj', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple',
        'email', 'mail', 'session', 'cookie', 'error', 'success', 'message', 'log',
        'test', 'debug', 'config', 'setting', 'option', 'param', 'arg', 'var',
        'get', 'set', 'add', 'remove', 'update', 'delete', 'create', 'read', 'write',
        'save', 'load', 'find', 'search', 'filter', 'map', 'reduce', 'sort',
        'min', 'max', 'sum', 'count', 'length', 'len', 'start', 'stop', 'begin', 'end',
    }
    # Check if text starts with a common English prefix and the rest is also English
    for prefix in sorted(english_word_prefixes, key=len, reverse=True):  # Check longer prefixes first
        if text_lower.startswith(prefix) and len(text_lower) > len(prefix):
            remainder = text_lower[len(prefix):]
            # Check if remainder is also a common English word
            if remainder in common_english_programming_terms or remainder in english_word_prefixes:
                return "English/ASCII"
            # Check if remainder matches common patterns (like "pass", "word", etc.)
            if re.match(r'^(pass|word|key|name|id|data|info|html|url|form|input|button|label|text|page|template|file|dir|path|code|func|method|class|obj|str|int|float|bool|list|dict|set|tuple|email|mail|session|cookie|error|success|message|log|test|debug|config|setting|option|param|arg|var|get|set|add|remove|update|delete|create|read|write|save|load|find|search|filter|map|reduce|sort|min|max|sum|count|length|len|start|stop|begin|end)$', remainder):
                return "English/ASCII"
    
    # Check if it's a compound identifier with underscores (e.g., "user_data", "html_template")
    if '_' in text_lower:
        words = text_lower.split('_')
        # If all words are common English programming terms, it's English
        if all(word in common_english_programming_terms or len(word) < 2 for word in words):
            return "English/ASCII"
        
        # Expanded list of common English programming prefixes
        common_english_prefixes = {
            'user', 'pass', 'admin', 'data', 'html', 'http', 'url', 'form', 'input', 'button', 
            'label', 'text', 'page', 'template', 'file', 'dir', 'path', 'code', 'func', 'method', 
            'class', 'obj', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 
            'email', 'login', 'session', 'cookie', 'error', 'success', 'message', 'info', 
            'name', 'id', 'key', 'value', 'type', 'style', 'title', 'head', 'body', 'div', 
            'span', 'p', 'a', 'img', 'script', 'link', 'meta', 'render', 'redirect', 'request',
            'response', 'secret', 'public', 'private', 'secure', 'config', 'setting', 'option', 'param',
            'arg', 'args', 'kwargs', 'var', 'variable', 'const', 'constant', 'temp', 'tmp',
            'init', 'setup', 'clean', 'validate', 'check', 'verify', 'test', 'debug', 'log',
            'get', 'set', 'add', 'remove', 'update', 'delete', 'create', 'read', 'write',
            'save', 'load', 'find', 'search', 'filter', 'map', 'reduce', 'sort', 'min', 'max',
            'sum', 'count', 'length', 'len', 'start', 'stop', 'begin', 'end', 'open', 'close',
            'ssn', 'social', 'security', 'number', 'num', 'digit', 'digits', 'last', 'first',
            'middle', 'full', 'partial', 'complete', 'empty', 'null', 'none', 'true', 'false',
            'jane', 'john', 'smith', 'doe',  # Common English names used in examples
        }
        
        # If it starts with a common English prefix
        if words[0] in common_english_prefixes:
            # Check if remaining words are also English programming terms or short/common words
            remaining_words = words[1:]
            if not remaining_words:  # Only one word (the prefix itself)
                return "English/ASCII"
            # If all remaining words are English terms or short (< 4 chars), it's English
            if all(word in common_english_programming_terms or len(word) < 4 for word in remaining_words):
                return "English/ASCII"
            # Also check if remaining words are common English words (like "last", "first", "key", etc.)
            common_english_suffixes = {
                'key', 'keys', 'value', 'values', 'data', 'info', 'name', 'names', 'id', 'ids',
                'type', 'types', 'class', 'classes', 'style', 'styles', 'title', 'titles',
                'last', 'first', 'middle', 'full', 'partial', 'complete', 'empty', 'null',
                'num', 'number', 'numbers', 'digit', 'digits', 'char', 'chars', 'string', 'strings',
                'list', 'lists', 'dict', 'dicts', 'set', 'sets', 'tuple', 'tuples',
                'page', 'pages', 'template', 'templates', 'view', 'views', 'form', 'forms',
                'input', 'inputs', 'button', 'buttons', 'label', 'labels', 'text', 'texts',
                'error', 'errors', 'success', 'message', 'messages', 'log', 'logs',
                'user', 'users', 'admin', 'admins', 'session', 'sessions', 'cookie', 'cookies',
                'file', 'files', 'dir', 'dirs', 'path', 'paths', 'url', 'urls',
                'html', 'http', 'https', 'email', 'emails', 'mail', 'mails',
                'smith', 'doe', 'jane', 'john',  # Common English names
            }
            if all(word in common_english_suffixes or word in common_english_programming_terms or len(word) < 4 for word in remaining_words):
                return "English/ASCII"
    
    # Try library-based language detection first (langdetect - similar to Google Translate)
    detected_lang = _detect_language_with_library(text)
    if detected_lang and detected_lang != "en":
        # Map language codes to script categories
        script = _map_language_to_script(detected_lang)
        if script and script != "English/ASCII":
            return script
    
    try:
        from language_detection import classify_string  # type: ignore
        
        # Try the standard classification (checks for non-ASCII characters)
        result = classify_string(text)
        script = result.get("script", "Unknown")
        
        # If classified as English/ASCII, check if it contains non-English words
        # This handles cases like Portuguese/Spanish identifiers that use ASCII characters
        if script == "English/ASCII":
            # Check if text contains non-English words (common in Portuguese, Spanish, etc.)
            if _contains_non_english_words(text):
                return "Other Non-English"
        
        return script
    except Exception:
        # Fallback: simple ASCII check
        try:
            text.encode("ascii")
            # Even if ASCII, check for non-English words
            if _contains_non_english_words(text):
                return "Other Non-English"
            return "English/ASCII"
        except Exception:
            return "Non-English"


def _detect_language_with_library(text: str) -> Optional[str]:
    """
    Use library-based language detection (langdetect, similar to Google Translate).
    Returns language code (e.g., 'pt', 'es', 'fr') or None if detection fails.
    
    Note: langdetect works better with longer text. For short identifiers,
    we rely more on the word dictionary approach.
    """
    try:
        from langdetect import detect, DetectorFactory, LangDetectException
        # Set seed for consistent results
        DetectorFactory.seed = 0
        
        # Skip very short text - langdetect is unreliable for single words or very short text
        # For identifiers (often single words or short phrases), use minimum length of 5
        text_clean = text.strip()
        if len(text_clean) < 5:
            return None
        
        # Comprehensive list of common English programming terms that should NEVER be detected as non-English
        common_english_programming_terms = {
            # User/auth related
            'user', 'users', 'username', 'usernames', 'user_data', 'user_data', 'user_name', 'user_name',
            'password', 'passwords', 'pass', 'pass1', 'pass2', 'pass123', 'password123',
            'admin', 'admin1', 'admin2', 'admins', 'administrator',
            'login', 'logout', 'log', 'logs', 'logged', 'logging',
            'auth', 'authentication', 'authorize', 'authorization',
            'session', 'sessions', 'cookie', 'cookies',
            # Data related
            'data', 'database', 'db', 'databases', 'data_base',
            'table', 'tables', 'row', 'rows', 'column', 'columns',
            'record', 'records', 'entry', 'entries',
            # Web/HTML related
            'html', 'html_template', 'html_page', 'html_content', 'html_string',
            'http', 'https', 'url', 'urls', 'uri', 'uris',
            'form', 'forms', 'input', 'inputs', 'button', 'buttons',
            'label', 'labels', 'text', 'texts', 'textarea', 'textareas',
            'submit', 'submits', 'reset', 'resets', 'required',
            'method', 'methods', 'action', 'actions', 'type', 'types',
            'name', 'names', 'id', 'ids', 'key', 'keys', 'value', 'values',
            'class', 'classes', 'style', 'styles', 'title', 'titles',
            'head', 'heads', 'body', 'bodies', 'div', 'divs', 'span', 'spans',
            'p', 'paragraph', 'paragraphs', 'a', 'link', 'links', 'href',
            'img', 'image', 'images', 'src', 'alt',
            'script', 'scripts', 'meta', 'metas', 'doctype',
            # Page/template related
            'page', 'pages', 'template', 'templates', 'view', 'views',
            'dashboard', 'dashboards', 'home', 'homes', 'index', 'indexes',
            'main', 'error', 'errors', 'success', 'message', 'messages',
            'info', 'information', 'content', 'contents',
            # File/system related
            'file', 'files', 'dir', 'directory', 'directories', 'path', 'paths',
            'code', 'codes', 'function', 'functions', 'method', 'methods',
            'class', 'classes', 'object', 'objects', 'instance', 'instances',
            # Data types
            'string', 'strings', 'str', 'int', 'integer', 'integers',
            'float', 'floats', 'bool', 'boolean', 'booleans',
            'list', 'lists', 'dict', 'dictionary', 'dictionaries',
            'set', 'sets', 'tuple', 'tuples',
            # Control flow
            'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally',
            'return', 'def', 'class', 'import', 'from', 'as',
            'true', 'false', 'none', 'null', 'undefined',
            # Common patterns
            'get', 'set', 'add', 'remove', 'update', 'delete', 'clear',
            'copy', 'clone', 'create', 'read', 'write', 'save', 'load',
            'find', 'search', 'filter', 'map', 'reduce', 'sort',
            'min', 'max', 'sum', 'count', 'length', 'len',
            'start', 'stop', 'begin', 'end', 'init', 'initialize',
            'test', 'tests', 'test1', 'test2', 'test_data',
            'config', 'configuration', 'settings', 'options',
            'request', 'requests', 'response', 'responses',
            'email', 'emails', 'mail', 'mails',
        }
        
        text_lower = text_clean.lower()
        
        # Check if it's a common English programming term
        if text_lower in common_english_programming_terms:
            return None
        
        # For single-word identifiers, check if it matches common patterns
        import re
        if len(text_clean.split()) == 1:
            # Single identifier - check if it's a common English pattern
            # Pattern: word + number (e.g., "user1", "pass123")
            if re.match(r'^(user|pass|admin|test|data|info|name|id|key|val|email|login|page|form|button|label|input|html|http|url|file|dir|path|code|func|method|class|obj|str|int|float|bool|list|dict|set|tuple)[0-9]*$', text_lower):
                return None
            # Pattern: word_word (e.g., "user_data", "html_template")
            if '_' in text_lower:
                words = text_lower.split('_')
                # If all words are common English programming terms, skip
                if all(word in common_english_programming_terms or len(word) < 2 for word in words):
                    return None
                # If it starts with common English prefix
                if words[0] in ['user', 'pass', 'admin', 'data', 'html', 'http', 'url', 'form', 'input', 'button', 'label', 'text', 'page', 'template', 'file', 'dir', 'path', 'code', 'func', 'method', 'class', 'obj', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'email', 'login', 'session', 'cookie', 'error', 'success', 'message', 'info', 'name', 'id', 'key', 'value', 'type', 'style', 'title', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'script', 'link', 'meta']:
                    # Check if the rest looks like English
                    if all(word in common_english_programming_terms or len(word) < 3 for word in words[1:]):
                        return None
            
            # For single identifiers, langdetect is very unreliable - skip if < 10 chars
            if len(text_clean) < 10:
                return None
        
        # Try to detect language
        detected = detect(text)
        
        # Additional filter: if detected language is not English but text contains common English words
        if detected and detected != 'en':
            # Check if text contains common English programming words
            words_in_text = re.findall(r'\b[a-z]+\b', text_lower)
            english_word_count = sum(1 for word in words_in_text if word in common_english_programming_terms)
            # If more than half the words are English programming terms, it's likely English
            if words_in_text and english_word_count > len(words_in_text) / 2:
                return None
        
        return detected
    except ImportError:
        # langdetect not installed
        return None
    except (LangDetectException, Exception):
        # Detection failed, return None to fall back to other methods
        return None


def _map_language_to_script(lang_code: str) -> str:
    """
    Map language code from langdetect to script category.
    Returns script name or None.
    """
    # Map common language codes to script categories
    language_to_script = {
        # Latin alphabet languages (will be "Other Non-English")
        'pt': 'Other Non-English',  # Portuguese
        'es': 'Other Non-English',  # Spanish
        'fr': 'Other Non-English',  # French
        'it': 'Other Non-English',  # Italian
        'de': 'Other Non-English',  # German
        'tr': 'Other Non-English',  # Turkish
        'pl': 'Other Non-English',  # Polish
        'nl': 'Other Non-English',  # Dutch
        'ro': 'Other Non-English',  # Romanian
        'hu': 'Other Non-English',  # Hungarian
        'cs': 'Other Non-English',  # Czech
        'sv': 'Other Non-English',  # Swedish
        'da': 'Other Non-English',  # Danish
        'fi': 'Other Non-English',  # Finnish
        'no': 'Other Non-English',  # Norwegian
        'vi': 'Other Non-English',  # Vietnamese
        'id': 'Other Non-English',  # Indonesian
        'ms': 'Other Non-English',  # Malay
        'th': 'Other Non-English',  # Thai
        # Non-Latin scripts
        'zh-cn': 'CJK Unified Ideographs',  # Chinese
        'zh': 'CJK Unified Ideographs',
        'ja': 'Japanese (Hiragana/Katakana/Kanji)',
        'ko': 'Hangul (Korean)',
        'ar': 'Arabic',
        'he': 'Hebrew',
        'hi': 'Devanagari (Hindi, etc.)',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'mr': 'Devanagari (Hindi, etc.)',
        'ur': 'Arabic',
        'ru': 'Cyrillic',
        'uk': 'Cyrillic',
        'el': 'Greek and Coptic',
    }
    
    lang_lower = lang_code.lower()
    return language_to_script.get(lang_lower, 'Other Non-English')


def _contains_non_english_words(text: str) -> bool:
    """
    Check if text contains words that are clearly non-English (Portuguese, Spanish, etc.).
    Splits on underscores and common separators to check individual words.
    """
    import re
    
    # Common non-English words in programming contexts (Portuguese, Spanish, French, etc.)
    # These are words that are unlikely to be English programming terms
    non_english_words = {
        # Portuguese
        'nome', 'usuario', 'usuário', 'usuarios', 'usuários',
        'numero', 'número', 'numeros', 'números',
        'seguranca', 'segurança', 'social',
        'ultimos', 'últimos', 'ultimo', 'último',
        'quatro', 'digitos', 'dígitos', 'digito', 'dígito',
        'senha', 'chave', 'dados', 'banco', 'dados',
        'pagina', 'página', 'informacoes', 'informações',
        'inicial', 'login', 'sessao', 'sessão',
        # Spanish
        'nombre', 'usuario', 'usuarios', 'numero', 'números',
        'seguridad', 'social', 'ultimos', 'últimos',
        'cuatro', 'digitos', 'dígitos', 'clave', 'datos',
        'pagina', 'página', 'informacion', 'información',
        'inicial', 'sesion', 'sesión',
        # French
        'nom', 'utilisateur', 'utilisateurs', 'numero', 'numéro',
        'securite', 'sécurité', 'social', 'derniers', 'dernier',
        'quatre', 'chiffres', 'chiffre', 'cle', 'clé', 'donnees', 'données',
        'page', 'information', 'informations', 'initiale', 'session',
        # Turkish
        'kullanici', 'kullanıcı', 'numara', 'guvenlik', 'güvenlik',
        'sosyal', 'son', 'dort', 'dört', 'rakam', 'rakamlar',
        'sifre', 'şifre', 'veri', 'veriler', 'sayfa', 'bilgi', 'bilgiler',
        'oturum', 'giris', 'giriş', 'eposta', 'adresi', 'adı', 'bilgileri',
        'gönder', 'goster', 'göster', 'sablonu', 'şablonu',
        # Other common non-English programming terms
        'benutzer', 'benutzername',  # German
        'utente', 'utenti',  # Italian
    }
    
    # Split text on underscores, hyphens, and camelCase boundaries
    # This handles identifiers like nome_usuario, numero-seguranca, etc.
    words = re.split(r'[_\-]|(?<=[a-z])(?=[A-Z])', text.lower())
    
    # Check each word component
    for word in words:
        # Remove numbers and special characters
        word_clean = re.sub(r'[^a-záéíóúãõçñüäö]', '', word.lower())
        if word_clean and len(word_clean) >= 3:  # Only check words of 3+ characters
            if word_clean in non_english_words:
                return True
    
    return False


def aggregate_counts(elements: Dict[str, List[str]]) -> Dict[str, Any]:
    categories = [
        "identifiers",
        "variables",
        "literals",
        "comments",
        "docstrings",
        "functions",
        "classes",
    ]

    overall = defaultdict(int)
    by_category = {cat: defaultdict(int) for cat in categories}

    for cat in categories:
        values = elements.get(cat, []) or []
        for value in values:
            script = classify_text(str(value))
            # Normalize to two buckets for overview; keep script names for detail
            bucket = "English/ASCII" if script == "English/ASCII" else script or "Non-English"
            overall[bucket] += 1
            by_category[cat][bucket] += 1

    return {
        "overall": dict(overall),
        "by_category": {k: dict(v) for k, v in by_category.items()},
    }


def plot_overall_pie(counts: Dict[str, int], out_path: str, title: str) -> None:
    if not counts:
        return
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    
    # Create labels with both count and percentage
    def make_autopct(values):
        def autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val})'
        return autopct
    
    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct=make_autopct(values), startangle=90)
    plt.axis("equal")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_category_bars(by_category: Dict[str, Dict[str, int]], out_path: str, title: str) -> None:
    categories = list(by_category.keys())
    # Collect all bucket names across categories
    all_buckets = sorted({b for v in by_category.values() for b in v.keys()}) or ["English/ASCII", "Non-English"]

    import numpy as np
    x = np.arange(len(categories))
    width = 0.8 / max(1, len(all_buckets))

    plt.figure(figsize=(14, 8))
    bars = []
    for i, bucket in enumerate(all_buckets):
        vals = [by_category.get(cat, {}).get(bucket, 0) for cat in categories]
        bar = plt.bar(x + i * width - (len(all_buckets)-1) * width / 2, vals, width=width, label=bucket)
        bars.append(bar)
        
        # Add count labels on top of bars
        for j, (bar_rect, val) in enumerate(zip(bar, vals)):
            if val > 0:  # Only show label if there's a value
                plt.text(bar_rect.get_x() + bar_rect.get_width()/2., bar_rect.get_height() + 0.1,
                        f'{val}', ha='center', va='bottom', fontsize=8)

    plt.xticks(x, categories, rotation=30, ha="right")
    plt.ylabel("Count")
    plt.title(title)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_detailed_summary_table(summary: Dict[str, Any]) -> str:
    """Create a detailed text summary table of the language analysis."""
    lines = []
    lines.append("=" * 80)
    lines.append("DETAILED LANGUAGE ANALYSIS SUMMARY")
    lines.append("=" * 80)
    
    for lang_key, data in summary.items():
        lines.append(f"\n[LANGUAGE] {lang_key.upper()}")
        lines.append("-" * 40)
        
        # Overall summary
        overall = data.get("overall", {})
        total_items = sum(overall.values())
        lines.append(f"Total Items: {total_items}")
        
        for script, count in sorted(overall.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_items * 100) if total_items > 0 else 0
            lines.append(f"  {script}: {count} items ({percentage:.1f}%)")
        
        # Category breakdown
        lines.append(f"\n[CATEGORY BREAKDOWN]:")
        by_category = data.get("by_category", {})
        for category, scripts in by_category.items():
            if scripts:  # Only show categories with data
                lines.append(f"  {category.title()}:")
                for script, count in sorted(scripts.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"    {script}: {count}")
    
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def run_visualization(input_path: str, charts_dir: str, summary_out: Optional[str] = None) -> None:
    os.makedirs(charts_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    results = parsed.get("results", {}) if isinstance(parsed, dict) else {}
    summary: Dict[str, Any] = {}

    print(f"Processing {len(results)} languages...")
    
    for lang_key, item in results.items():
        if not item or not item.get("success"):
            print(f"Skipping {lang_key} (no successful parsing)")
            continue
            
        print(f"Processing {lang_key}...")
        elements = item.get("elements", {}) or {}
        counts = aggregate_counts(elements)
        summary[lang_key] = counts

        # Charts per language
        pie_path = os.path.join(charts_dir, f"{lang_key}_overall_pie.png")
        plot_overall_pie(counts["overall"], pie_path, f"Overall Script Distribution: {lang_key}")

        bars_path = os.path.join(charts_dir, f"{lang_key}_by_category.png")
        plot_category_bars(counts["by_category"], bars_path, f"Script Distribution by Category: {lang_key}")

    # Create overall comparison chart
    if summary:
        create_overall_comparison_chart(summary, charts_dir)

    # Create detailed summary
    detailed_summary = create_detailed_summary_table(summary)
    print("\n" + detailed_summary)

    # Save summary JSON with enhanced data
    if summary_out:
        enhanced_summary = {
            "summary": summary,
            "detailed_analysis": detailed_summary,
            "total_languages": len(summary),
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
        with open(summary_out, "w", encoding="utf-8") as f:
            json.dump(enhanced_summary, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Saved charts to: {charts_dir}")
    if summary_out:
        print(f"[SUCCESS] Saved enhanced summary to: {summary_out}")


def create_overall_comparison_chart(summary: Dict[str, Any], charts_dir: str) -> None:
    """Create an overall comparison chart across all languages."""
    import numpy as np
    
    languages = list(summary.keys())
    all_scripts = set()
    
    # Collect all unique scripts
    for data in summary.values():
        overall = data.get("overall", {})
        all_scripts.update(overall.keys())
    
    all_scripts = sorted(list(all_scripts))
    
    # Create data matrix
    data_matrix = []
    for lang in languages:
        overall = summary[lang].get("overall", {})
        row = [overall.get(script, 0) for script in all_scripts]
        data_matrix.append(row)
    
    data_matrix = np.array(data_matrix)
    
    # Create stacked bar chart
    plt.figure(figsize=(16, 10))
    x = np.arange(len(languages))
    width = 0.8
    
    bottom = np.zeros(len(languages))
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_scripts)))
    
    for i, script in enumerate(all_scripts):
        values = data_matrix[:, i]
        if np.any(values > 0):  # Only plot if there are values
            plt.bar(x, values, width, bottom=bottom, label=script, color=colors[i])
            
            # Add count labels on bars
            for j, (val, bot) in enumerate(zip(values, bottom)):
                if val > 0:
                    plt.text(j, bot + val/2, f'{int(val)}', ha='center', va='center', 
                            fontsize=8, fontweight='bold')
            
            bottom += values
    
    plt.xlabel('Languages')
    plt.ylabel('Count')
    plt.title('Script Distribution Across All Languages')
    plt.xticks(x, languages, rotation=45, ha='right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    comparison_path = os.path.join(charts_dir, "overall_comparison.png")
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[SUCCESS] Created overall comparison chart: {comparison_path}")


def main() -> None:
    project_root = os.path.abspath(os.path.dirname(__file__))
    ensure_mlp_on_path(project_root)

    input_path = os.path.join(project_root, "data", "llm_parsed.json")
    charts_dir = os.path.join(project_root, "data", "language_charts")
    summary_out = os.path.join(project_root, "data", "non_english_summary.json")
    run_visualization(input_path, charts_dir, summary_out)


if __name__ == "__main__":
    main()



