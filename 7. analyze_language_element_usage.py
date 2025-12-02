"""
Language Element Usage Statistics Script

Analyzes how much of each code element type (literals, variables, comments, 
docstrings, classes, functions) has been used in each prompt for each language.

Usage:
    python analyze_language_element_usage.py
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Language codes in order
LANGUAGE_CODES = ["en", "zh-CN", "hi", "es", "ar", "fr", "bn", "pt", "ru", "id", "ur", "de", "ja", "mr", "vi", "te", "ha", "tr"]
ELEMENT_TYPES = ["literals", "docstrings", "comments", "variables", "functions", "classes"]

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


def extract_element_counts(lang_data: Dict, elem_type: str) -> Dict[str, int]:
    """
    Extract element counts for a language-element pair.
    
    Returns:
        Dictionary with script types and their counts
    """
    if not lang_data:
        return {}
    
    by_category = lang_data.get('by_category', {})
    category_data = by_category.get(elem_type, {})
    
    return dict(category_data)


def analyze_prompt(prompt_num: int, data_dir: str = "data") -> Tuple[Optional[Dict], Dict]:
    """
    Analyze element usage for a single prompt.
    
    Returns:
        (results_dict, statistics_dict)
        - results_dict: {language: {element_type: {script: count}}}
        - statistics_dict: aggregated stats for this prompt
    """
    prompt_dir = os.path.join(data_dir, f"prompt_{prompt_num}")
    summary_path = os.path.join(prompt_dir, "non_english_summary.json")
    
    if not os.path.exists(summary_path):
        return None, {}
    
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        results = {}
        stats = {
            'total_elements': 0,
            'by_element': {elem: 0 for elem in ELEMENT_TYPES},
            'by_language': {lang: 0 for lang in LANGUAGE_CODES}
        }
        
        for lang_code in LANGUAGE_CODES:
            lang_data = summary.get(lang_code)
            results[lang_code] = {}
            
            if not lang_data:
                # Missing language - all zeros
                for elem_type in ELEMENT_TYPES:
                    results[lang_code][elem_type] = {}
                continue
            
            by_category = lang_data.get('by_category', {})
            
            for elem_type in ELEMENT_TYPES:
                category_data = by_category.get(elem_type, {})
                
                # Get all counts (both English and non-English)
                element_counts = extract_element_counts(lang_data, elem_type)
                results[lang_code][elem_type] = element_counts
                
                # Calculate total for this element type
                total_count = sum(element_counts.values())
                
                # Update statistics
                stats['total_elements'] += total_count
                stats['by_element'][elem_type] += total_count
                stats['by_language'][lang_code] += total_count
        
        return results, stats
        
    except json.JSONDecodeError as e:
        return None, {'error': f"JSON decode error: {e}"}
    except Exception as e:
        return None, {'error': f"Error: {e}"}


def analyze_all_prompts(data_dir: str = "data", max_prompts: int = 150) -> Dict:
    """
    Analyze all prompts and generate comprehensive statistics.
    
    Returns:
        Dictionary with analysis results
    """
    print("="*80)
    print("LANGUAGE ELEMENT USAGE STATISTICS")
    print("="*80)
    
    # Find all prompt folders
    prompt_folders = []
    for i in range(1, max_prompts + 1):
        prompt_dir = os.path.join(data_dir, f"prompt_{i}")
        if os.path.exists(prompt_dir):
            prompt_folders.append(i)
    
    print(f"\nFound {len(prompt_folders)} prompt folders: {prompt_folders[:10]}...")
    print(f"Analyzing {len(prompt_folders)} prompts...\n")
    
    all_results = {}
    all_stats = {
        'total_prompts': len(prompt_folders),
        'successful_prompts': 0,
        'failed_prompts': 0,
        'by_language': {lang: {
            'total': 0,
            'by_element': {elem: {'total': 0, 'per_prompt': []} for elem in ELEMENT_TYPES},
            'prompts_analyzed': 0
        } for lang in LANGUAGE_CODES},
        'by_element': {elem: {
            'total': 0,
            'by_language': {lang: 0 for lang in LANGUAGE_CODES},
            'per_prompt': []
        } for elem in ELEMENT_TYPES},
        'prompt_details': {}
    }
    
    # Analyze each prompt
    for prompt_num in prompt_folders:
        results, stats = analyze_prompt(prompt_num, data_dir)
        
        if results is None:
            all_stats['failed_prompts'] += 1
            if 'error' in stats:
                print(f"[FAILED] Prompt {prompt_num}: {stats['error']}")
            continue
        
        all_results[prompt_num] = results
        all_stats['successful_prompts'] += 1
        
        # Aggregate statistics
        for lang_code in LANGUAGE_CODES:
            lang_results = results.get(lang_code, {})
            lang_total = 0
            
            for elem_type in ELEMENT_TYPES:
                elem_counts = lang_results.get(elem_type, {})
                elem_total = sum(elem_counts.values())
                
                # Update language-level stats
                all_stats['by_language'][lang_code]['total'] += elem_total
                all_stats['by_language'][lang_code]['by_element'][elem_type]['total'] += elem_total
                all_stats['by_language'][lang_code]['by_element'][elem_type]['per_prompt'].append(elem_total)
                lang_total += elem_total
                
                # Update element-level stats
                all_stats['by_element'][elem_type]['total'] += elem_total
                all_stats['by_element'][elem_type]['by_language'][lang_code] += elem_total
                all_stats['by_element'][elem_type]['per_prompt'].append(elem_total)
            
            if lang_total > 0:
                all_stats['by_language'][lang_code]['prompts_analyzed'] += 1
        
        # Store prompt details
        all_stats['prompt_details'][prompt_num] = stats
    
    return {
        'results': all_results,
        'statistics': all_stats
    }


def print_statistics_report(analysis_data: Dict):
    """Print a comprehensive statistics report."""
    stats = analysis_data['statistics']
    
    print("\n" + "="*80)
    print("ELEMENT USAGE STATISTICS REPORT")
    print("="*80)
    
    # Overall statistics
    print(f"\n[OVERALL] SUMMARY:")
    print(f"  Total prompts analyzed: {stats['successful_prompts']}")
    print(f"  Failed prompts: {stats['failed_prompts']}")
    
    # Statistics by language
    print(f"\n[BY LANGUAGE] ELEMENT USAGE PER LANGUAGE:")
    print(f"\n{'Language':<20} {'Total':<10} {'Literals':<10} {'Docstrings':<12} {'Comments':<10} {'Variables':<10} {'Functions':<10} {'Classes':<10}")
    print("-" * 100)
    
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
        
        if lang_stats['prompts_analyzed'] == 0:
            continue
        
        # Calculate averages
        literals_avg = np.mean(lang_stats['by_element']['literals']['per_prompt']) if lang_stats['by_element']['literals']['per_prompt'] else 0
        docstrings_avg = np.mean(lang_stats['by_element']['docstrings']['per_prompt']) if lang_stats['by_element']['docstrings']['per_prompt'] else 0
        comments_avg = np.mean(lang_stats['by_element']['comments']['per_prompt']) if lang_stats['by_element']['comments']['per_prompt'] else 0
        variables_avg = np.mean(lang_stats['by_element']['variables']['per_prompt']) if lang_stats['by_element']['variables']['per_prompt'] else 0
        functions_avg = np.mean(lang_stats['by_element']['functions']['per_prompt']) if lang_stats['by_element']['functions']['per_prompt'] else 0
        classes_avg = np.mean(lang_stats['by_element']['classes']['per_prompt']) if lang_stats['by_element']['classes']['per_prompt'] else 0
        
        print(f"{lang_name:<20} {lang_stats['total']:<10.0f} "
              f"{literals_avg:<10.2f} {docstrings_avg:<12.2f} {comments_avg:<10.2f} "
              f"{variables_avg:<10.2f} {functions_avg:<10.2f} {classes_avg:<10.2f}")
    
    # Detailed statistics by language
    print(f"\n[BY LANGUAGE] DETAILED STATISTICS:")
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
        
        if lang_stats['prompts_analyzed'] == 0:
            continue
        
        print(f"\n  {lang_name} ({lang_code}):")
        print(f"    Prompts analyzed: {lang_stats['prompts_analyzed']}")
        print(f"    Total elements: {lang_stats['total']}")
        
        for elem_type in ELEMENT_TYPES:
            elem_stats = lang_stats['by_element'][elem_type]
            if elem_stats['total'] > 0:
                avg = np.mean(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
                min_val = min(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
                max_val = max(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
                print(f"      {elem_type:12s}: Total={elem_stats['total']:5d}, "
                      f"Avg={avg:6.2f}, Min={min_val:3.0f}, Max={max_val:3.0f}")
    
    # Statistics by element type
    print(f"\n[BY ELEMENT] ELEMENT USAGE ACROSS ALL LANGUAGES:")
    for elem_type in ELEMENT_TYPES:
        elem_stats = stats['by_element'][elem_type]
        if elem_stats['total'] > 0:
            avg = np.mean(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
            min_val = min(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
            max_val = max(elem_stats['per_prompt']) if elem_stats['per_prompt'] else 0
            
            print(f"\n  {elem_type.upper()}:")
            print(f"    Total across all languages: {elem_stats['total']}")
            print(f"    Average per prompt: {avg:.2f}")
            print(f"    Min per prompt: {min_val:.0f}, Max per prompt: {max_val:.0f}")
            
            # Top languages for this element type
            lang_totals = [(lang, count) for lang, count in elem_stats['by_language'].items() if count > 0]
            lang_totals.sort(key=lambda x: x[1], reverse=True)
            
            print(f"    Top 5 languages:")
            for lang_code, count in lang_totals[:5]:
                lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
                pct = 100 * count / elem_stats['total']
                print(f"      {lang_name:15s} ({lang_code:5s}): {count:5d} ({pct:5.2f}%)")
    
    # Prompt-level summary
    print(f"\n[PROMPTS] PROMPT-LEVEL SUMMARY:")
    print(f"  Prompts with most element usage:")
    prompt_totals = []
    for prompt_num, details in stats['prompt_details'].items():
        if details.get('total_elements', 0) > 0:
            prompt_totals.append((prompt_num, details['total_elements']))
    
    prompt_totals.sort(key=lambda x: x[1], reverse=True)
    for prompt_num, total in prompt_totals[:10]:
        print(f"    Prompt {prompt_num:3d}: {total:5d} total elements")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


def save_detailed_report(analysis_data: Dict, output_file: str = "data/language_element_usage_report.json"):
    """Save detailed statistics to JSON file."""
    stats = analysis_data['statistics']
    
    # Convert to JSON-serializable format
    report = {
        'summary': {
            'total_prompts': stats['total_prompts'],
            'successful_prompts': stats['successful_prompts'],
            'failed_prompts': stats['failed_prompts']
        },
        'by_language': {},
        'by_element': {}
    }
    
    # Language statistics
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        if lang_stats['prompts_analyzed'] > 0:
            lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
            report['by_language'][lang_code] = {
                'name': lang_name,
                'prompts_analyzed': lang_stats['prompts_analyzed'],
                'total_elements': lang_stats['total'],
                'by_element': {}
            }
            
            for elem_type in ELEMENT_TYPES:
                elem_stats = lang_stats['by_element'][elem_type]
                if elem_stats['total'] > 0:
                    report['by_language'][lang_code]['by_element'][elem_type] = {
                        'total': elem_stats['total'],
                        'average': float(np.mean(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                        'min': float(min(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                        'max': float(max(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                        'per_prompt': elem_stats['per_prompt']
                    }
    
    # Element statistics
    for elem_type in ELEMENT_TYPES:
        elem_stats = stats['by_element'][elem_type]
        if elem_stats['total'] > 0:
            report['by_element'][elem_type] = {
                'total': elem_stats['total'],
                'average': float(np.mean(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                'min': float(min(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                'max': float(max(elem_stats['per_prompt'])) if elem_stats['per_prompt'] else 0,
                'by_language': {lang: count for lang, count in elem_stats['by_language'].items() if count > 0}
            }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] Detailed report saved to: {output_file}")
    except Exception as e:
        print(f"\n[WARNING] Could not save report: {e}")


def main():
    """Main entry point."""
    # Analyze all prompts
    analysis_data = analyze_all_prompts(data_dir="data", max_prompts=150)
    
    # Print comprehensive report
    print_statistics_report(analysis_data)
    
    # Save detailed report
    save_detailed_report(analysis_data)


if __name__ == "__main__":
    main()

