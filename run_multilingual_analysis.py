"""
Multilingual Analysis Pipeline - Main Orchestrator

This script orchestrates the complete multilingual analysis pipeline:
1. Parses and summarizes each prompt (Tree-sitter + visualization)
2. Runs global analysis (heatmap, element usage, verification)

Usage:
    python run_multilingual_analysis.py
    python run_multilingual_analysis.py --data_path data/ --max_prompts 50
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List

# Import our modules
from parse_and_non_english import parse_and_summarize_prompt
from multilingual_analysis import (
    build_heatmap_grid,
    analyze_element_usage,
    verify_heatmap_data
)


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
            llm_output_path = item / "llm_output.json"
            if llm_output_path.exists():
                prompt_folders.append(item)
    
    # Sort by folder name (prompt_1, prompt_2, etc.)
    prompt_folders.sort(key=lambda x: x.name)
    
    return prompt_folders


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run complete multilingual analysis pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_multilingual_analysis.py
  python run_multilingual_analysis.py --data_path data/ --max_prompts 50
  python run_multilingual_analysis.py --skip_global  # Only per-prompt analysis
        """
    )
    parser.add_argument(
        '--data_path',
        type=str,
        default='data',
        help='Path to data directory containing prompt folders (default: data)'
    )
    parser.add_argument(
        '--max_prompts',
        type=int,
        default=None,
        help='Maximum number of prompts to process (default: all found)'
    )
    parser.add_argument(
        '--skip_global',
        action='store_true',
        help='Skip global analysis (only run per-prompt parsing/visualization)'
    )
    parser.add_argument(
        '--skip_per_prompt',
        action='store_true',
        help='Skip per-prompt analysis (only run global analysis)'
    )
    
    args = parser.parse_args()
    
    # Determine paths
    project_root = Path(__file__).parent
    data_dir = project_root / args.data_path
    
    print(f"\n{'='*70}")
    print("MULTILINGUAL ANALYSIS PIPELINE")
    print("="*70)
    print(f"Data directory: {data_dir}")
    print(f"Project root: {project_root}")
    
    # Step 1: Find prompt folders
    print(f"\n{'='*70}")
    print("STEP 1: Finding prompt folders")
    print("="*70)
    
    prompt_folders = find_prompt_folders(data_dir)
    
    if not prompt_folders:
        print(f"\nNo prompt folders with llm_output.json found in {data_dir}")
        print("Please ensure you have run pipeline_min.py first to generate llm_output.json files")
        sys.exit(1)
    
    # Limit prompts if specified
    if args.max_prompts and args.max_prompts < len(prompt_folders):
        prompt_folders = prompt_folders[:args.max_prompts]
        print(f"Limiting to first {args.max_prompts} prompts")
    
    print(f"\nFound {len(prompt_folders)} prompt folder(s):")
    for folder in prompt_folders[:10]:
        print(f"  - {folder.name}")
    if len(prompt_folders) > 10:
        print(f"  ... and {len(prompt_folders) - 10} more")
    
    # Step 2: Process each prompt (parsing + visualization)
    if not args.skip_per_prompt:
        print(f"\n{'='*70}")
        print("STEP 2: Parsing and summarizing prompts")
        print("="*70)
        
        successful = 0
        failed = 0
        
        for i, prompt_dir in enumerate(prompt_folders, 1):
            print(f"\n[{i}/{len(prompt_folders)}] Processing: {prompt_dir.name}")
            
            if parse_and_summarize_prompt(prompt_dir, project_root):
                successful += 1
            else:
                failed += 1
        
        print(f"\n{'='*70}")
        print("PER-PROMPT PROCESSING COMPLETE")
        print("="*70)
        print(f"Successfully processed: {successful}/{len(prompt_folders)} folders")
        if failed > 0:
            print(f"Failed: {failed} folder(s)")
    else:
        print(f"\n{'='*70}")
        print("STEP 2: SKIPPED (--skip_per_prompt)")
        print("="*70)
    
    # Step 3: Global analysis
    if not args.skip_global:
        print(f"\n{'='*70}")
        print("STEP 3: Running global analysis")
        print("="*70)
        
        # 3a. Build heatmap grid
        print(f"\n[3a] Building heatmap grid...")
        try:
            heatmap_path = build_heatmap_grid(
                str(data_dir),
                output_path=str(data_dir / "heatmap_grid.png"),
                num_prompts=args.max_prompts
            )
            print(f"  ✓ Heatmap saved: {heatmap_path}")
        except Exception as e:
            print(f"  ✗ Error building heatmap: {e}")
            import traceback
            traceback.print_exc()
        
        # 3b. Analyze element usage
        print(f"\n[3b] Analyzing element usage...")
        try:
            element_usage_result = analyze_element_usage(
                data_dir=str(data_dir),
                max_prompts=args.max_prompts or 150
            )
            print(f"  ✓ Element usage analysis complete")
            print(f"  ✓ Report saved: {element_usage_result.get('report_path', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Error analyzing element usage: {e}")
            import traceback
            traceback.print_exc()
        
        # 3c. Verify heatmap data
        print(f"\n[3c] Verifying heatmap data...")
        try:
            verification_result = verify_heatmap_data(
                data_dir=str(data_dir),
                max_prompts=args.max_prompts or 150
            )
            print(f"  ✓ Verification complete")
            print(f"  ✓ Report saved: {verification_result.get('report_path', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Error verifying heatmap data: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*70}")
        print("GLOBAL ANALYSIS COMPLETE")
        print("="*70)
    else:
        print(f"\n{'='*70}")
        print("STEP 3: SKIPPED (--skip_global)")
        print("="*70)
    
    # Final summary
    print(f"\n{'='*70}")
    print("PIPELINE COMPLETE")
    print("="*70)
    print(f"Results saved in: {data_dir}")
    print(f"  - Per-prompt: llm_parsed.json, non_english_summary.json, language_charts/")
    print(f"  - Global: heatmap_grid.png, language_element_usage_report.json, heatmap_verification_report.json")
    print("="*70)


if __name__ == "__main__":
    main()

