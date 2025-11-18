# Code Validation Pipeline

## Overview

The Code Validation Pipeline is a comprehensive feature that validates generated code by checking:

1. **Code Execution**: Tests if the code runs properly or returns any errors
2. **Prompt Understanding**: Analyzes if the LLM understood the prompt correctly
3. **Code Relevance**: Checks if the generated code is relevant to the original prompt
4. **Language Detection**: Detects spoken languages (non-English) in code with specific locations and instances

## Features

### 1. Code Execution Testing
- **Syntax Checking**: Validates Python syntax before execution
- **Runtime Testing**: Executes code in a safe, isolated environment
- **Error Detection**: Captures and categorizes errors (SyntaxError, RuntimeError, TimeoutError, etc.)
- **Output Capture**: Records stdout and stderr from code execution

### 2. Prompt Understanding Analysis
- **Keyword Matching**: Extracts key terms from the prompt and checks if they appear in code
- **Semantic Analysis**: Uses heuristics to determine if code addresses prompt requirements
- **Confidence Scoring**: Provides a confidence score (0-1) indicating how well the prompt was understood
- **Missing Elements**: Identifies which key requirements might be missing from the code

### 3. Code Relevance Checking
- **Semantic Overlap**: Calculates word overlap between prompt and code
- **Relevance Score**: Provides a relevance score (0-1) indicating how relevant the code is
- **Stop Word Filtering**: Removes common programming and English stop words for better analysis

### 4. Language Detection with Locations
- **Multi-Element Detection**: Scans comments, docstrings, string literals, and identifiers
- **Location Tracking**: Records exact line numbers and categories for each detected instance
- **Script Classification**: Identifies specific scripts (Chinese, Arabic, Hindi, etc.)
- **Confidence Scoring**: Provides confidence scores for each detection

## Usage

### Standalone Usage

Run validation on a specific prompt directory:

```bash
python code_validation_pipeline.py data/prompt_1
```

### Integrated Usage

The validation pipeline is automatically integrated into the main pipeline. When you run:

```bash
python pipeline.py prompts_input.json
```

The validation step will run automatically after code parsing and visualization.

### Output

The validation results are saved to `code_validation.json` in each prompt directory. The file contains:

```json
{
  "prompt_directory": "data/prompt_1",
  "original_prompt": "...",
  "summary": {
    "total_languages": 19,
    "successful_executions": 15,
    "average_overall_score": 0.75,
    "languages_with_errors": ["ar", "de"],
    "languages_with_non_english": ["zh-CN", "hi", "ja", "ar"]
  },
  "detailed_results": {
    "en": {
      "language": "en",
      "code_length": 1234,
      "execution": {
        "success": true,
        "error_type": null,
        "error_message": null,
        "execution_time": 0.05,
        "output": "..."
      },
      "prompt_understanding": {
        "understood": true,
        "confidence": 0.85,
        "reasoning": "...",
        "missing_elements": []
      },
      "code_relevance": {
        "relevant": true,
        "relevance_score": 0.72,
        "reasoning": "..."
      },
      "language_detection": {
        "CJK Unified Ideographs": [
          {
            "text": "...",
            "location": "Line 5 (comment)",
            "category": "comment",
            "confidence": 0.95
          }
        ]
      },
      "overall_score": 0.86
    }
  }
}
```

## Example Output

When running the validation pipeline, you'll see output like:

```
Processing validation for: data/prompt_1
============================================================
Validating code for en...
Validating code for zh-CN...
Validating code for hi...
...

============================================================
VALIDATION SUMMARY
============================================================
Total languages processed: 19
Successful executions: 15
Average overall score: 75.23%
Languages with errors: 4
Languages with non-English text: 8

Languages with execution errors:
  - ar: RuntimeError - Import error: module not found
  - de: SyntaxError - Invalid syntax on line 3

Languages with non-English text detected:
  - zh-CN: CJK Unified Ideographs (3 instances)
      Line 2 (comment): 将多个字节从一个内存位置复制...
      Line 5 (docstring): 参数: dest: 目标内存位置...
  - hi: Devanagari (Hindi, etc.) (2 instances)
      Line 3 (comment): कई बाइट्स को एक मेमोरी...
```

## Integration Points

The validation pipeline integrates with:

1. **Main Pipeline** (`pipeline.py`): Automatically runs after code parsing
2. **Language Detection** (`Multi_language_parser/language_detection.py`): Uses existing language detection infrastructure
3. **Code Parsing** (`parser.py`): Works with parsed code outputs

## Customization

### Adjusting Timeout

Modify the execution timeout in `code_validation_pipeline.py`:

```python
execute_code(code, code_language="python", timeout=30)  # 30 seconds
```

### Enhancing Prompt Understanding

The current implementation uses keyword matching. You can enhance it by:

1. Using LLM-based analysis for better semantic understanding
2. Adding more sophisticated NLP techniques
3. Implementing domain-specific requirement extraction

### Improving Language Detection

The language detection can be enhanced by:

1. Adding more Unicode script ranges
2. Using more sophisticated language detection libraries (e.g., `langdetect`, `polyglot`)
3. Implementing context-aware detection

## Limitations

1. **Code Execution**: Currently only supports Python. Other languages would need additional execution handlers.
2. **Safety**: Code execution is done in isolated subprocesses, but be cautious with malicious code.
3. **Prompt Understanding**: Uses heuristic-based analysis. For production use, consider LLM-based semantic analysis.
4. **Language Detection**: Focuses on script-based detection. Some languages may not be detected if they use Latin script.

## Future Enhancements

Potential improvements:

1. **Multi-language Execution**: Support for JavaScript, Java, C++, etc.
2. **LLM-based Analysis**: Use LLMs to evaluate prompt understanding and relevance
3. **Test Case Generation**: Automatically generate and run test cases
4. **Performance Metrics**: Measure code performance (execution time, memory usage)
5. **Security Analysis**: Detect potential security vulnerabilities
6. **Code Quality Metrics**: Analyze code complexity, maintainability, etc.

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:
- `Multi_language_parser` is in the Python path
- All dependencies from `requirements.txt` are installed

### Execution Timeouts

If code execution times out:
- Increase the timeout value
- Check if the code has infinite loops
- Verify the code doesn't require user input

### Language Detection Issues

If language detection isn't working:
- Verify `language_detection.py` is accessible
- Check that code contains actual non-English text
- Ensure Unicode characters are properly encoded

## Contributing

To extend the validation pipeline:

1. Add new validation functions to `code_validation_pipeline.py`
2. Integrate them into `validate_code_for_language()`
3. Update the output schema in `process_prompt_directory()`
4. Add tests for new functionality


