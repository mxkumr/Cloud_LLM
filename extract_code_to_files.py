"""
Extract code from llm_output.json files and save as individual language files.

This script:
1. Scans all prompt folders in data/ directory
2. Reads llm_output.json from each folder
3. Extracts code for each language
4. Saves as <language_code>.py files in the same prompt folder

Usage:
    python extract_code_to_files.py
    python extract_code_to_files.py data/prompt_1  # Process specific folder
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Optional


def sanitize_filename(lang_code: str) -> str:
    """
    Convert language code to a valid filename.
    Handles special cases like 'zh-CN' -> 'zh_CN.py'
    """
    # Replace hyphens with underscores for filename safety
    safe_name = lang_code.replace('-', '_')
    return f"{safe_name}.py"


def extract_code_from_json(json_path: Path, prompt_dir: Path) -> dict:
    """
    Extract code from llm_output.json and save as individual files.
    
    Returns:
        Dictionary with extraction results: {lang_code: success_status}
    """
    results = {}
    
    try:
        # Load JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            print(f"  ⚠ Warning: {json_path} does not contain a dictionary")
            return results
        
        # Process each language
        for lang_code, code_content in data.items():
            if code_content is None:
                print(f"  ⚠ Skipping {lang_code}: code is None")
                results[lang_code] = False
                continue
            
            if not isinstance(code_content, str) or not code_content.strip():
                print(f"  ⚠ Skipping {lang_code}: empty or invalid code")
                results[lang_code] = False
                continue
            
            # Create safe filename
            filename = sanitize_filename(lang_code)
            output_path = prompt_dir / filename
            
            try:
                # Write code to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(code_content)
                
                results[lang_code] = True
                print(f"  ✓ Saved: {filename} ({len(code_content)} chars)")
                
            except Exception as e:
                print(f"  ✗ Error saving {lang_code}: {e}")
                results[lang_code] = False
        
        return results
        
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON decode error: {e}")
        return results
    except Exception as e:
        print(f"  ✗ Error reading {json_path}: {e}")
        return results


def process_single_prompt_folder(prompt_dir: Path) -> bool:
    """
    Process a single prompt folder.
    
    Returns:
        True if successful, False otherwise
    """
    folder_name = prompt_dir.name
    json_path = prompt_dir / "llm_output.json"
    
    if not json_path.exists():
        print(f"  ⚠ {folder_name}: llm_output.json not found")
        return False
    
    print(f"\n{'='*60}")
    print(f"Processing: {folder_name}")
    print(f"Path: {prompt_dir}")
    print(f"{'='*60}")
    
    results = extract_code_from_json(json_path, prompt_dir)
    
    if not results:
        print(f"  ✗ No code extracted from {folder_name}")
        return False
    
    # Summary
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n  Summary: {successful}/{total} language files created")
    
    return successful > 0


def find_prompt_folders(data_dir: Path) -> List[Path]:
    """
    Find all prompt folders containing llm_output.json.
    
    Returns:
        List of Path objects for prompt directories
    """
    prompt_folders = []
    
    if not data_dir.exists():
        return prompt_folders
    
    # Scan for prompt_* directories
    for item in data_dir.iterdir():
        if item.is_dir() and item.name.startswith('prompt_'):
            json_path = item / "llm_output.json"
            if json_path.exists():
                prompt_folders.append(item)
    
    # Sort by folder name (prompt_1, prompt_2, etc.)
    prompt_folders.sort(key=lambda x: x.name)
    
    return prompt_folders


def main():
    """Main entry point."""
    # Determine data directory
    if len(sys.argv) > 1:
        # Specific folder provided
        target_path = Path(sys.argv[1])
        if target_path.is_dir():
            # Process single folder
            if (target_path / "llm_output.json").exists():
                process_single_prompt_folder(target_path)
            else:
                print(f"Error: llm_output.json not found in {target_path}")
                sys.exit(1)
        else:
            print(f"Error: {target_path} is not a directory")
            sys.exit(1)
    else:
        # Process all prompt folders in data/
        project_root = Path(__file__).parent
        data_dir = project_root / "data"
        
        print(f"\n{'='*60}")
        print("Extract Code to Files")
        print("="*60)
        print(f"Scanning: {data_dir}")
        
        prompt_folders = find_prompt_folders(data_dir)
        
        if not prompt_folders:
            print(f"\nNo prompt folders with llm_output.json found in {data_dir}")
            print("Please ensure you have run pipeline_min.py first")
            return
        
        print(f"\nFound {len(prompt_folders)} prompt folder(s):")
        for folder in prompt_folders:
            print(f"  - {folder.name}")
        
        # Process each folder
        successful = 0
        failed = 0
        
        for prompt_dir in prompt_folders:
            if process_single_prompt_folder(prompt_dir):
                successful += 1
            else:
                failed += 1
        
        # Final summary
        print(f"\n{'='*60}")
        print("EXTRACTION COMPLETE")
        print("="*60)
        print(f"Successfully processed: {successful}/{len(prompt_folders)} folders")
        if failed > 0:
            print(f"Failed: {failed} folder(s)")
        print(f"\nCode files saved in individual prompt folders under: {data_dir}")
        print("="*60)


if __name__ == "__main__":
    main()

