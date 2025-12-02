"""
Generate CSV from Code Validation Results

This script processes all prompt folders and generates a CSV file containing
all validation tables, categorized by prompt name.

Usage:
    python generate_validation_csv.py
"""

import os
import json
import csv
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


def extract_table_data_from_detailed_results(detailed_results: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract table data from detailed_results when summary_table is not available.
    
    Returns:
        List of dictionaries representing table rows
    """
    rows = []
    
    for lang_code, result in detailed_results.items():
        execution = result.get('execution', {})
        syntax = result.get('syntax', {})
        prompt_comp = result.get('prompt_comparison', {})
        multilingual = result.get('multilingual_detection', {})
        
        # Code Worked status
        if execution.get('success', False) and syntax.get('valid', False):
            code_worked = "✓ Yes"
        elif not syntax.get('valid', False):
            code_worked = "✗ Syntax Error"
        elif not execution.get('success', False):
            code_worked = "✗ Runtime Error"
        else:
            code_worked = "? Unknown"
        
        # Understood Prompt status
        if prompt_comp:
            if prompt_comp.get('similar', False):
                similarity = prompt_comp.get('similarity_score', 0) * 100
                understood_prompt = f"✓ Yes ({similarity:.0f}%)"
            else:
                similarity = prompt_comp.get('similarity_score', 0) * 100
                understood_prompt = f"✗ No ({similarity:.0f}%)"
        else:
            understood_prompt = "- N/A"
        
        # Multilingual Code status
        if multilingual.get('detected', False):
            locations = multilingual.get('locations', [])
            
            # Group locations by language and category
            lang_category_map = {}
            for loc in locations:
                loc_lang = loc.get('language', 'Unknown')
                loc_category = loc.get('category', 'unknown')
                
                if loc_lang and loc_lang != 'Unknown':
                    if loc_lang not in lang_category_map:
                        lang_category_map[loc_lang] = {}
                    if loc_category not in lang_category_map[loc_lang]:
                        lang_category_map[loc_lang][loc_category] = 0
                    lang_category_map[loc_lang][loc_category] += 1
            
            # Build display string
            lang_displays = []
            for loc_lang, categories in sorted(lang_category_map.items()):
                total_instances = sum(categories.values())
                short_lang_name = loc_lang.replace('Mandarin ', '').replace('Standard ', '')
                if len(short_lang_name) > 10:
                    short_lang_name = short_lang_name[:10]
                
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
                lang_display = f"{short_lang_name}:{total_instances} ({categories_str})"
                lang_displays.append(lang_display)
            
            if len(lang_displays) == 1:
                multilingual_code = f"✓ Yes ({lang_displays[0]})"
            elif len(lang_displays) <= 2:
                multilingual_code = f"✓ Yes ({'; '.join(lang_displays)})"
            else:
                total_langs = len(lang_category_map)
                total_instances = len(locations)
                multilingual_code = f"✓ Yes ({'; '.join(lang_displays[:2])} +{total_langs-2} more)"
            
            # Truncate if too long
            if len(multilingual_code) > 45:
                multilingual_code = multilingual_code[:42] + "..."
        else:
            multilingual_code = "✗ No"
        
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
            issues_str = "; ".join(issues[:2])
            if len(issues) > 2:
                issues_str += f" (+{len(issues) - 2} more)"
        else:
            issues_str = "- None"
        
        rows.append({
            'language': lang_code,
            'code_worked': code_worked,
            'understood_prompt': understood_prompt,
            'multilingual_code': multilingual_code,
            'issues': issues_str
        })
    
    return rows


def process_prompt_folder(prompt_dir: str) -> Optional[List[Dict[str, str]]]:
    """
    Process a single prompt folder and extract table data.
    
    Returns:
        List of dictionaries representing table rows, or None if error
    """
    prompt_name = os.path.basename(prompt_dir)
    validation_path = os.path.join(prompt_dir, "code_validation.json")
    
    try:
        with open(validation_path, 'r', encoding='utf-8') as f:
            validation_data = json.load(f)
        
        # Try to parse summary_table first
        summary_table_str = validation_data.get('summary_table', '')
        if summary_table_str:
            rows = parse_summary_table(summary_table_str)
            if rows:
                # Add prompt name to each row
                for row in rows:
                    row['prompt_name'] = prompt_name
                return rows
        
        # Fallback to detailed_results if summary_table is not available or empty
        detailed_results = validation_data.get('detailed_results', {})
        if detailed_results:
            rows = extract_table_data_from_detailed_results(detailed_results)
            # Add prompt name to each row
            for row in rows:
                row['prompt_name'] = prompt_name
            return rows
        
        return None
        
    except FileNotFoundError:
        print(f"  ✗ {prompt_name}: code_validation.json not found")
        return None
    except json.JSONDecodeError as e:
        print(f"  ✗ {prompt_name}: Invalid JSON - {e}")
        return None
    except Exception as e:
        print(f"  ✗ {prompt_name}: Error - {e}")
        return None


def generate_csv(data_dir: str, output_path: str) -> None:
    """
    Generate CSV file with all validation tables.
    
    Args:
        data_dir: Path to data directory
        output_path: Path to output CSV file
    """
    prompt_folders = find_prompt_folders(data_dir)
    
    if not prompt_folders:
        print(f"No prompt folders with code_validation.json found in {data_dir}")
        return
    
    print(f"Found {len(prompt_folders)} prompt folder(s) to process")
    
    # Collect all rows
    all_rows = []
    
    for prompt_dir in prompt_folders:
        prompt_name = os.path.basename(prompt_dir)
        print(f"Processing {prompt_name}...")
        
        rows = process_prompt_folder(prompt_dir)
        if rows:
            all_rows.extend(rows)
            print(f"  ✓ Processed {prompt_name} ({len(rows)} languages)")
        else:
            print(f"  ✗ {prompt_name}: No data extracted")
    
    if not all_rows:
        print("\n✗ No data to write to CSV")
        return
    
    # Write to CSV
    fieldnames = ['prompt_name', 'language', 'code_worked', 'understood_prompt', 
                  'multilingual_code', 'issues']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by prompt name, then by language for better organization
        all_rows_sorted = sorted(all_rows, key=lambda x: (x['prompt_name'], x['language']))
        
        for row in all_rows_sorted:
            # Ensure all fields are present
            csv_row = {
                'prompt_name': row.get('prompt_name', ''),
                'language': row.get('language', ''),
                'code_worked': row.get('code_worked', ''),
                'understood_prompt': row.get('understood_prompt', ''),
                'multilingual_code': row.get('multilingual_code', ''),
                'issues': row.get('issues', '')
            }
            writer.writerow(csv_row)
    
    print(f"\n✓ CSV file generated: {output_path}")
    print(f"  Total rows: {len(all_rows)}")
    print(f"  Total prompts: {len(set(row['prompt_name'] for row in all_rows))}")


def main():
    """Main entry point."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    output_path = os.path.join(data_dir, "all_validation_tables.csv")
    
    print(f"\n{'='*60}")
    print("Code Validation CSV Generator")
    print("="*60)
    print(f"Data directory: {data_dir}")
    print(f"Output file: {output_path}\n")
    
    generate_csv(data_dir, output_path)
    
    print(f"\n{'='*60}")
    print("Generation Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()


