"""
Small Multiples Heatmap Grid Visualization

Creates a 3×2 grid of heatmaps showing English (1) vs Non-English (0) 
for 6 code element types across 150 prompts and 18 languages.

Usage:
    python "5. Overall_graph_visualize.py"
    
    Or with custom data:
    python "5. Overall_graph_visualize.py" --data_path data/
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Union
import argparse


# Language code to name mapping (18 languages)
LANG_CODE_TO_NAME = {
    "en": "English",
    "zh-CN": "Chinese",
    "hi": "Hindi",
    "es": "Spanish",
    "ar": "Arabic",
    "fr": "French",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "id": "Indonesian",
    "ur": "Urdu",
    "de": "German",
    "ja": "Japanese",
    "mr": "Marathi",
    "vi": "Vietnamese",
    "te": "Telugu",
    "ha": "Hausa",
    "tr": "Turkish",
}

# Language codes in order (18 languages)
LANGUAGE_CODES = list(LANG_CODE_TO_NAME.keys())

# Element types in order (6 types)
ELEMENT_TYPES = ["literals", "docstrings", "comments", "variables", "functions", "classes"]


def load_data_from_prompts(data_dir: str, num_prompts: Optional[int] = None) -> np.ndarray:
    """
    Load data from prompt folders and create a 3D array.
    
    Args:
        data_dir: Path to data directory
        num_prompts: Number of prompts to process (None = use all found)
    
    Returns:
        numpy array of shape (6, num_prompts, 18) where:
        - First dimension: 6 element types
        - Second dimension: prompts (0-indexed in array, but represents actual prompt numbers)
        - Third dimension: 18 languages
        - Values: 1 = English, 0 = Non-English
    """
    # Find all prompt folders dynamically (don't assume they start from 1)
    prompt_folders = []
    prompt_numbers = []
    
    # Scan for all prompt_* folders
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            if item.startswith('prompt_'):
                try:
                    prompt_num = int(item.split('_')[1])
                    prompt_dir = os.path.join(data_dir, item)
                    if os.path.isdir(prompt_dir):
                        prompt_folders.append((prompt_num, prompt_dir))
                        prompt_numbers.append(prompt_num)
                except (ValueError, IndexError):
                    continue
    
    # Sort by prompt number
    prompt_folders.sort(key=lambda x: x[0])
    prompt_numbers.sort()
    
    if not prompt_folders:
        print(f"Warning: No prompt folders found in {data_dir}")
        return np.ones((6, 1, 18), dtype=np.float32)
    
    # Determine the actual range
    min_prompt = min(prompt_numbers)
    max_prompt = max(prompt_numbers)
    actual_num_prompts = len(prompt_folders)
    
    print(f"Found {actual_num_prompts} prompt folders (range: {min_prompt}-{max_prompt})")
    
    # Use actual number of prompts found, or limit to num_prompts if specified
    if num_prompts is not None and num_prompts < actual_num_prompts:
        prompt_folders = prompt_folders[:num_prompts]
        actual_num_prompts = num_prompts
        print(f"Limiting to first {num_prompts} prompts")
    
    # Initialize array with 1 (English by default) using actual number of prompts
    data_array = np.ones((6, actual_num_prompts, 18), dtype=np.float32)
    
    # Create mapping from prompt number to array index
    prompt_to_idx = {prompt_num: idx for idx, (prompt_num, _) in enumerate(prompt_folders)}
    
    # Statistics tracking
    stats = {
        'total_cells': 0,
        'non_english_cells': 0,
        'by_element': {elem: {'total': 0, 'non_english': 0} for elem in ELEMENT_TYPES}
    }
    
    # Process each prompt folder
    for prompt_num, prompt_dir in prompt_folders:
        prompt_idx = prompt_to_idx[prompt_num]  # Get array index for this prompt
        summary_path = os.path.join(prompt_dir, "non_english_summary.json")
        
        if not os.path.exists(summary_path):
            continue
        
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            
            # Process each language
            for lang_idx, lang_code in enumerate(LANGUAGE_CODES):
                lang_data = summary.get(lang_code)
                
                if not lang_data:
                    continue
                
                by_category = lang_data.get('by_category', {})
                
                # Check each element type
                for elem_idx, elem_type in enumerate(ELEMENT_TYPES):
                    category_data = by_category.get(elem_type, {})
                    
                    # Check if there's any non-English content
                    has_non_english = any(
                        script != 'English/ASCII' and count > 0
                        for script, count in category_data.items()
                    )
                    
                    # Set to 0 if non-English found, otherwise keep 1 (English)
                    if has_non_english:
                        data_array[elem_idx, prompt_idx, lang_idx] = 0.0
                        stats['non_english_cells'] += 1
                        stats['by_element'][elem_type]['non_english'] += 1
                    
                    stats['total_cells'] += 1
                    stats['by_element'][elem_type]['total'] += 1
        
        except Exception as e:
            print(f"Error processing {prompt_dir}: {e}")
            continue
    
    # Print statistics
    if stats['total_cells'] > 0:
        print(f"\nData Statistics:")
        print(f"  Total cells processed: {stats['total_cells']}")
        print(f"  Non-English cells: {stats['non_english_cells']} ({100*stats['non_english_cells']/stats['total_cells']:.2f}%)")
        print(f"\n  By Element Type:")
        for elem_type in ELEMENT_TYPES:
            elem_stats = stats['by_element'][elem_type]
            if elem_stats['total'] > 0:
                pct = 100 * elem_stats['non_english'] / elem_stats['total']
                print(f"    {elem_type:12s}: {elem_stats['non_english']:4d}/{elem_stats['total']:4d} ({pct:5.2f}%)")
    
    return data_array


def generate_dummy_data(num_prompts: int = 50, num_languages: int = 18) -> np.ndarray:
    """
    Generate dummy data for testing.
    
    Args:
        num_prompts: Number of prompts
        num_languages: Number of languages
    
    Returns:
        numpy array of shape (6, num_prompts, num_languages)
    """
    # Create random binary data with some patterns
    np.random.seed(42)
    
    # Base probability of non-English (0) varies by element type
    non_english_probs = {
        0: 0.1,  # literals - 10% non-English
        1: 0.3,  # docstrings - 30% non-English
        2: 0.4,  # comments - 40% non-English
        3: 0.05, # variables - 5% non-English
        4: 0.02, # functions - 2% non-English
        5: 0.01, # classes - 1% non-English
    }
    
    data = np.ones((6, num_prompts, num_languages), dtype=np.float32)
    
    for elem_idx in range(6):
        prob = non_english_probs.get(elem_idx, 0.1)
        # Create some clustering - some prompts/languages more likely to have non-English
        mask = np.random.random((num_prompts, num_languages)) < prob
        data[elem_idx][mask] = 0.0
    
    return data


def create_heatmap_grid(
    data: np.ndarray,
    output_path: Optional[str] = None,
    use_dummy_labels: bool = False
) -> None:
    """
    Create a 3×2 grid of heatmaps.
    
    Args:
        data: numpy array of shape (6, num_prompts, num_languages)
        output_path: Path to save the figure (optional)
        use_dummy_labels: If True, use simple numeric labels for testing
    """
    num_prompts, num_languages = data.shape[1], data.shape[2]
    
    # Create figure with 3×2 subplot grid
    fig, axes = plt.subplots(3, 2, figsize=(24, 18))
    fig.suptitle('English vs Non-English Code Elements Across Prompts and Languages',
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Element type titles
    element_titles = [
        "Literals",
        "Docstrings",
        "Comments",
        "Variables",
        "Functions",
        "Classes"
    ]
    
    # Language names for x-axis
    if use_dummy_labels:
        lang_labels = [f"L{i+1}" for i in range(num_languages)]
    else:
        lang_labels = [LANG_CODE_TO_NAME.get(code, code) for code in LANGUAGE_CODES[:num_languages]]
    
    # Create each heatmap
    for idx, (elem_idx, title) in enumerate(zip(range(6), element_titles)):
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        # Extract data for this element type
        heatmap_data = data[elem_idx, :, :]
        
        # Create heatmap using imshow with binary/diverging colormap
        # Using 'RdYlGn_r' (Red-Yellow-Green reversed) for clear binary distinction
        # Red = Non-English (0), Green = English (1)
        im = ax.imshow(heatmap_data, aspect='auto', cmap='RdYlGn_r', 
                      vmin=0, vmax=1, interpolation='nearest')
        
        # Set title
        ax.set_title(title, fontsize=14, fontweight='bold', pad=10)
        
        # Set x-axis labels (languages)
        ax.set_xticks(np.arange(num_languages))
        ax.set_xticklabels(lang_labels, rotation=45, ha='right', fontsize=8)
        ax.set_xlabel('Languages', fontsize=10, fontweight='bold')
        
        # Set y-axis labels (prompts)
        if num_prompts <= 50:
            # Show all prompt numbers
            step = max(1, num_prompts // 20)  # Show ~20 labels
            y_ticks = np.arange(0, num_prompts, step)
            y_labels = [f"{i+1}" for i in y_ticks]
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_labels, fontsize=7)
        else:
            # For more prompts, show fewer labels
            step = max(1, num_prompts // 15)
            y_ticks = np.arange(0, num_prompts, step)
            y_labels = [f"{i+1}" for i in y_ticks]
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_labels, fontsize=7)
        
        ax.set_ylabel('Prompts', fontsize=10, fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('English (1) / Non-English (0)', fontsize=9, rotation=270, labelpad=15)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['Non-English', 'English'])
        
        # Add grid for better readability
        ax.set_xticks(np.arange(num_languages) - 0.5, minor=True)
        ax.set_yticks(np.arange(num_prompts) - 0.5, minor=True)
        ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n[SUCCESS] Heatmap grid saved to: {output_path}")
    else:
        plt.show()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Create Small Multiples Heatmap Grid')
    parser.add_argument('--data_path', type=str, default='data',
                       help='Path to data directory containing prompt folders')
    parser.add_argument('--num_prompts', type=int, default=None,
                       help='Number of prompts to process (default: None = use all found)')
    parser.add_argument('--dummy', action='store_true',
                       help='Use dummy data instead of loading from files')
    parser.add_argument('--output', type=str, default='data/heatmap_grid.png',
                       help='Output path for the heatmap (default: data/heatmap_grid.png)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("SMALL MULTIPLES HEATMAP GRID VISUALIZATION")
    print("="*70)
    
    # Load or generate data
    if args.dummy:
        print(f"\nGenerating dummy data for {args.num_prompts} prompts × 18 languages...")
        data = generate_dummy_data(args.num_prompts, 18)
        use_dummy_labels = True
    else:
        print(f"\nLoading data from: {args.data_path}")
        data = load_data_from_prompts(args.data_path, args.num_prompts)
        use_dummy_labels = False
        print(f"Data shape: {data.shape}")
        print(f"  - Element types: {data.shape[0]}")
        print(f"  - Prompts: {data.shape[1]}")
        print(f"  - Languages: {data.shape[2]}")
    
    # Create heatmap grid
    print(f"\nCreating heatmap grid...")
    create_heatmap_grid(data, args.output, use_dummy_labels)
    
    print("\n" + "="*70)
    print("Visualization Complete!")
    print("="*70)


if __name__ == "__main__":
    # Example usage with dummy data (uncomment to test)
    # data = generate_dummy_data(150, 18)
    # create_heatmap_grid(data, "data/heatmap_grid_dummy.png", use_dummy_labels=True)
    
    main()

