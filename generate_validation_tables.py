"""
Generate JSON Tables from Code Validation Results

This script processes all prompt folders and generates structured JSON tables
displaying the validation results for each prompt.

Usage:
    python generate_validation_tables.py
"""

import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime


def find_prompt_folders(data_dir: str) -> List[str]:
    """
    Find all prompt folders in the data directory.
    Returns a list of folder paths that contain code_validation.json.
    """
    prompt_folders = []
    
    if not os.path.exists(data_dir):
        print(f"Data directory not found: {data_dir}")
        return prompt_folders
    
    # Scan all subdirectories in data/
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        
        # Check if it's a directory and contains code_validation.json
        if os.path.isdir(item_path):
            validation_path = os.path.join(item_path, "code_validation.json")
            if os.path.exists(validation_path):
                prompt_folders.append(item_path)
    
    # Sort folders for consistent processing order
    prompt_folders.sort()
    return prompt_folders


def parse_summary_table(table_string: str) -> List[Dict[str, str]]:
    """
    Parse the summary table string into structured data.
    
    Returns:
        List of dictionaries, each representing a row in the table
    """
    rows = []
    lines = table_string.split('\n')
    
    # Find the header row (line with column names)
    header_line = None
    separator_line_idx = None
    
    for i, line in enumerate(lines):
        if 'Language' in line and 'Code Worked' in line:
            header_line = line
            separator_line_idx = i + 1
            break
    
    if not header_line:
        return rows
    
    # Extract data rows (skip header, separator, and footer lines)
    for line in lines[separator_line_idx + 1:]:
        # Skip separator lines and empty lines
        if not line.strip() or line.strip().startswith('=') or line.strip().startswith('-'):
            continue
        
        # Parse the row using fixed-width parsing
        # Format: Language (15) Code Worked (15) Understood Prompt (20) Multilingual Code (40) Issues (20)
        if len(line) < 15:
            continue
        
        try:
            language = line[0:15].strip()
            code_worked = line[15:30].strip()
            understood_prompt = line[30:50].strip()
            multilingual_code = line[50:90].strip()
            issues = line[90:110].strip() if len(line) > 90 else ""
            
            # Only add if we have a valid language code
            if language and language != 'Language':
                rows.append({
                    'language': language,
                    'code_worked': code_worked,
                    'understood_prompt': understood_prompt,
                    'multilingual_code': multilingual_code,
                    'issues': issues
                })
        except Exception as e:
            # Skip malformed rows
            continue
    
    return rows


def extract_table_data_from_validation(validation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured table data from validation results.
    
    Returns:
        Dictionary with table data and summary statistics
    """
    # Parse the summary table string
    summary_table_str = validation_data.get('summary_table', '')
    table_rows = parse_summary_table(summary_table_str)
    
    # Get summary statistics
    summary = validation_data.get('summary', {})
    detailed_results = validation_data.get('detailed_results', {})
    
    # Build structured table data
    table_data = {
        'prompt_directory': validation_data.get('prompt_directory', ''),
        'generated_at': validation_data.get('generated_at', ''),
        'summary_statistics': {
            'total_languages': summary.get('total_languages', 0),
            'successful': summary.get('successful', 0),
            'syntax_errors': summary.get('syntax_errors', 0),
            'runtime_errors': summary.get('runtime_errors', 0),
            'success_rate': summary.get('success_rate', 0.0),
            'prompt_comparison': summary.get('prompt_comparison', {}),
            'multilingual_detection': summary.get('multilingual_detection', {})
        },
        'table_rows': table_rows,
        'detailed_table': []
    }
    
    # Also create a more detailed table with additional information from detailed_results
    for lang_code, result in detailed_results.items():
        execution = result.get('execution', {})
        syntax = result.get('syntax', {})
        prompt_comp = result.get('prompt_comparison', {})
        multilingual = result.get('multilingual_detection', {})
        
        detailed_row = {
            'language': lang_code,
            'code_length': result.get('code_length', 0),
            'status': result.get('status', 'unknown'),
            'syntax_valid': syntax.get('valid', False),
            'execution_success': execution.get('success', False),
            'execution_time': execution.get('execution_time', 0.0),
            'prompt_similarity_score': prompt_comp.get('similarity_score', 0.0) if prompt_comp else 0.0,
            'prompt_similar': prompt_comp.get('similar', False) if prompt_comp else False,
            'multilingual_detected': multilingual.get('detected', False),
            'multilingual_locations_count': len(multilingual.get('locations', [])),
            'error_type': syntax.get('error_type') or execution.get('error_type'),
            'error_message': syntax.get('error_message') or execution.get('error_message')
        }
        
        table_data['detailed_table'].append(detailed_row)
    
    return table_data


def process_all_prompts(data_dir: str) -> Dict[str, Any]:
    """
    Process all prompt folders and generate consolidated JSON tables.
    
    Returns:
        Dictionary containing all prompts' table data
    """
    prompt_folders = find_prompt_folders(data_dir)
    
    if not prompt_folders:
        print(f"No prompt folders with code_validation.json found in {data_dir}")
        return {}
    
    all_tables = {
        'generated_at': datetime.now().isoformat(),
        'total_prompts': len(prompt_folders),
        'prompts': {}
    }
    
    print(f"Found {len(prompt_folders)} prompt folder(s) to process")
    
    for prompt_dir in prompt_folders:
        prompt_name = os.path.basename(prompt_dir)
        validation_path = os.path.join(prompt_dir, "code_validation.json")
        
        print(f"Processing {prompt_name}...")
        
        try:
            with open(validation_path, 'r', encoding='utf-8') as f:
                validation_data = json.load(f)
            
            # Extract table data
            table_data = extract_table_data_from_validation(validation_data)
            all_tables['prompts'][prompt_name] = table_data
            
            print(f"  ✓ Processed {prompt_name} ({len(table_data['table_rows'])} languages)")
            
        except FileNotFoundError:
            print(f"  ✗ {prompt_name}: code_validation.json not found")
        except json.JSONDecodeError as e:
            print(f"  ✗ {prompt_name}: Invalid JSON - {e}")
        except Exception as e:
            print(f"  ✗ {prompt_name}: Error - {e}")
    
    return all_tables


def generate_individual_tables(data_dir: str, output_dir: Optional[str] = None) -> None:
    """
    Generate individual JSON table files for each prompt.
    
    Args:
        data_dir: Path to data directory
        output_dir: Optional output directory (defaults to data_dir)
    """
    if output_dir is None:
        output_dir = data_dir
    
    prompt_folders = find_prompt_folders(data_dir)
    
    if not prompt_folders:
        print(f"No prompt folders with code_validation.json found in {data_dir}")
        return
    
    print(f"Generating individual table files for {len(prompt_folders)} prompt(s)...")
    
    for prompt_dir in prompt_folders:
        prompt_name = os.path.basename(prompt_dir)
        validation_path = os.path.join(prompt_dir, "code_validation.json")
        
        try:
            with open(validation_path, 'r', encoding='utf-8') as f:
                validation_data = json.load(f)
            
            # Extract table data
            table_data = extract_table_data_from_validation(validation_data)
            
            # Save individual table file
            output_path = os.path.join(prompt_dir, "validation_table.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(table_data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Generated table for {prompt_name}")
            
        except Exception as e:
            print(f"  ✗ {prompt_name}: Error - {e}")


def main():
    """Main entry point."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    
    print(f"\n{'='*60}")
    print("Code Validation Tables Generator")
    print("="*60)
    print(f"Data directory: {data_dir}\n")
    
    # Generate consolidated tables
    print("Generating consolidated tables...")
    all_tables = process_all_prompts(data_dir)
    
    if all_tables.get('prompts'):
        # Save consolidated file
        consolidated_path = os.path.join(data_dir, "all_validation_tables.json")
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            json.dump(all_tables, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Consolidated tables saved to: {consolidated_path}")
        print(f"  Total prompts: {all_tables['total_prompts']}")
        
        # Generate individual table files
        print("\nGenerating individual table files...")
        generate_individual_tables(data_dir)
        
        print(f"\n{'='*60}")
        print("Generation Complete!")
        print(f"{'='*60}")
        print(f"✓ Consolidated file: {consolidated_path}")
        print(f"✓ Individual files: validation_table.json in each prompt folder")
        print(f"{'='*60}\n")
    else:
        print("\n✗ No validation data found. Please run code validation pipeline first.")


if __name__ == "__main__":
    main()

