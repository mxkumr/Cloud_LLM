"""
Parse and Visualize Pipeline

This pipeline processes existing llm_output.json files in prompt folders,
parses them, and generates visualizations.

Usage:
    python pipeline_parse_visualize.py

Features:
    - Scans data/ directory for prompt folders (e.g., data/prompt_1, data/prompt_2)
    - Parses llm_output.json in each folder using Tree-sitter
    - Generates language charts and summaries
    - Stores results in the same folder (llm_parsed.json, language_charts/, non_english_summary.json)
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List


def ensure_dirs() -> str:
    """Ensure data directory exists and return project root."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return project_root


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


def parse_llm_outputs(outputs: Dict[str, str]) -> Dict[str, Any]:
    """Parse LLM outputs using Tree-sitter."""
    from parser import parse_code_files_with_multilang_parser
    print("Parsing code snippets with Tree-sitter...")
    return parse_code_files_with_multilang_parser(outputs)


def visualize_language_distribution_for_prompt(prompt_dir: str) -> None:
    """Generate language charts for a specific prompt directory."""
    import non_english
    print("Generating language charts...")
    input_path = os.path.join(prompt_dir, "llm_parsed.json")
    charts_dir = os.path.join(prompt_dir, "language_charts")
    summary_out = os.path.join(prompt_dir, "non_english_summary.json")
    non_english.run_visualization(input_path, charts_dir, summary_out)


def process_single_prompt_folder(prompt_dir: str) -> bool:
    """
    Process a single prompt folder: parse llm_output.json and visualize.
    
    Args:
        prompt_dir: Path to the prompt folder (e.g., data/prompt_1)
    
    Returns:
        True if processing was successful, False otherwise
    """
    folder_name = os.path.basename(prompt_dir)
    llm_output_path = os.path.join(prompt_dir, "llm_output.json")
    
    print(f"\n{'='*60}")
    print(f"Processing folder: {folder_name}")
    print(f"Path: {prompt_dir}")
    print(f"{'='*60}")
    
    # Check if llm_output.json exists
    if not os.path.exists(llm_output_path):
        print(f"Warning: llm_output.json not found in {prompt_dir}")
        return False
    
    try:
        # Load llm_output.json
        print(f"Loading llm_output.json from {llm_output_path}...")
        with open(llm_output_path, "r", encoding="utf-8") as f:
            llm_outputs = json.load(f)
        
        if not isinstance(llm_outputs, dict):
            print(f"Error: llm_output.json does not contain a dictionary")
            return False
        
        # Filter out None values
        valid_outputs = {k: v for k, v in llm_outputs.items() if v is not None}
        
        if not valid_outputs:
            print(f"Warning: No valid outputs found in llm_output.json")
            return False
        
        print(f"Found {len(valid_outputs)} language outputs to parse")
        
        # Parse LLM outputs
        parsed = parse_llm_outputs(valid_outputs)
        
        # Save parsed results
        parsed_path = os.path.join(prompt_dir, "llm_parsed.json")
        with open(parsed_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print(f"Saved parsed results to {parsed_path}")
        
        # Check if parsing was successful
        if not parsed.get("success", False):
            print(f"Warning: Parsing completed with errors. Check {parsed_path} for details.")
        else:
            results = parsed.get("results", {})
            successful_parses = sum(1 for r in results.values() if r and r.get("success", False))
            print(f"Successfully parsed {successful_parses}/{len(results)} language outputs")
        
        # Visualize
        visualize_language_distribution_for_prompt(prompt_dir)
        
        print(f"Completed processing for folder: {folder_name}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file: {e}")
        return False
    except Exception as e:
        print(f"Error processing folder {folder_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main() -> None:
    """Main function to process all prompt folders."""
    project_root = ensure_dirs()
    data_dir = os.path.join(project_root, "data")
    
    print(f"\n{'='*60}")
    print("Parse and Visualize Pipeline")
    print("="*60)
    print(f"Scanning data directory: {data_dir}")
    
    # Find all prompt folders
    prompt_folders = find_prompt_folders(data_dir)
    
    if not prompt_folders:
        print(f"\nNo prompt folders with llm_output.json found in {data_dir}")
        print("Please ensure you have run pipeline_min.py or pipeline.py first to generate llm_output.json files")
        return
    
    print(f"\nFound {len(prompt_folders)} prompt folder(s) to process:")
    for folder in prompt_folders:
        print(f"  - {os.path.basename(folder)}")
    
    # Process each folder
    successful = 0
    failed = 0
    
    for i, prompt_dir in enumerate(prompt_folders, 1):
        print(f"\n{'='*60}")
        print(f"Processing folder {i}/{len(prompt_folders)}")
        print(f"{'='*60}")
        
        if process_single_prompt_folder(prompt_dir):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print("Processing Complete!")
    print(f"{'='*60}")
    print(f"Successfully processed: {successful}/{len(prompt_folders)} folders")
    if failed > 0:
        print(f"Failed: {failed} folder(s)")
    print(f"\nResults saved in individual folders under: {data_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

