"""
Comprehensive Verification Script for Heatmap Data

Verifies that the heatmap data extraction is correct by checking all prompts
and comparing expected values with the source data.

Usage:
    python verify_heatmap_data.py
"""

import os
import json
import numpy as np
from typing import Dict, List, Tuple, Optional

# Language codes in order (must match 5. Overall_graph_visualize.py)
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


def extract_expected_value(lang_data: Dict, elem_type: str) -> Tuple[float, Optional[Dict]]:
    """
    Extract expected value for a language-element pair.
    
    Returns:
        (value, non_english_details)
        - value: 0.0 if non-English found, 1.0 if English only
        - non_english_details: dict of non-English scripts found, or None
    """
    if not lang_data:
        return 1.0, None  # Missing data defaults to English
    
    by_category = lang_data.get('by_category', {})
    category_data = by_category.get(elem_type, {})
    
    # Check if there's any non-English content
    non_english_scripts = {
        script: count 
        for script, count in category_data.items() 
        if script != 'English/ASCII' and count > 0
    }
    
    if non_english_scripts:
        return 0.0, non_english_scripts
    else:
        return 1.0, None


def verify_prompt(prompt_num: int, data_dir: str = "data") -> Tuple[Optional[Dict], List[str], Dict]:
    """
    Verify data extraction for a single prompt.
    
    Returns:
        (results_dict, issues_list, statistics_dict)
    """
    prompt_dir = os.path.join(data_dir, f"prompt_{prompt_num}")
    summary_path = os.path.join(prompt_dir, "non_english_summary.json")
    
    if not os.path.exists(summary_path):
        return None, [f"File not found: {summary_path}"], {}
    
    try:
        with open(summary_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        results = {}
        issues = []
        stats = {
            'total_cells': 0,
            'english_cells': 0,
            'non_english_cells': 0,
            'missing_languages': [],
            'by_element': {elem: {'english': 0, 'non_english': 0} for elem in ELEMENT_TYPES}
        }
        
        for lang_idx, lang_code in enumerate(LANGUAGE_CODES):
            lang_data = summary.get(lang_code)
            results[lang_code] = {}
            
            if not lang_data:
                # Missing language data - should default to 1 (English)
                stats['missing_languages'].append(lang_code)
                for elem_type in ELEMENT_TYPES:
                    results[lang_code][elem_type] = 1.0
                    stats['total_cells'] += 1
                    stats['english_cells'] += 1
                    stats['by_element'][elem_type]['english'] += 1
                continue
            
            by_category = lang_data.get('by_category', {})
            
            for elem_idx, elem_type in enumerate(ELEMENT_TYPES):
                category_data = by_category.get(elem_type, {})
                
                expected_value, non_english_details = extract_expected_value(lang_data, elem_type)
                results[lang_code][elem_type] = expected_value
                
                stats['total_cells'] += 1
                if expected_value == 0.0:
                    stats['non_english_cells'] += 1
                    stats['by_element'][elem_type]['non_english'] += 1
                else:
                    stats['english_cells'] += 1
                    stats['by_element'][elem_type]['english'] += 1
                
                # Log non-English cases for detailed reporting
                if non_english_details:
                    issues.append({
                        'language': lang_code,
                        'element': elem_type,
                        'scripts': non_english_details
                    })
        
        return results, issues, stats
        
    except json.JSONDecodeError as e:
        return None, [f"JSON decode error: {e}"], {}
    except Exception as e:
        return None, [f"Error: {e}"], {}


def verify_all_prompts(data_dir: str = "data", max_prompts: int = 150) -> Dict:
    """
    Verify all prompts and generate comprehensive report.
    
    Returns:
        Dictionary with verification results
    """
    print("="*80)
    print("COMPREHENSIVE HEATMAP DATA VERIFICATION")
    print("="*80)
    
    # Find all prompt folders
    prompt_folders = []
    for i in range(1, max_prompts + 1):
        prompt_dir = os.path.join(data_dir, f"prompt_{i}")
        if os.path.exists(prompt_dir):
            prompt_folders.append(i)
    
    print(f"\nFound {len(prompt_folders)} prompt folders: {prompt_folders[:10]}...")
    print(f"Verifying {len(prompt_folders)} prompts...\n")
    
    all_results = {}
    all_issues = []
    all_stats = {
        'total_prompts': len(prompt_folders),
        'successful_prompts': 0,
        'failed_prompts': 0,
        'total_cells': 0,
        'english_cells': 0,
        'non_english_cells': 0,
        'missing_languages_count': {},
        'missing_languages_prompts': {},  # Track which prompts are missing each language
        'by_element': {elem: {'english': 0, 'non_english': 0} for elem in ELEMENT_TYPES},
        'prompt_details': {}
    }
    
    # Verify each prompt
    for prompt_num in prompt_folders:
        results, issues, stats = verify_prompt(prompt_num, data_dir)
        
        if results is None:
            all_stats['failed_prompts'] += 1
            print(f"✗ Prompt {prompt_num}: FAILED - {issues[0] if issues else 'Unknown error'}")
            continue
        
        all_results[prompt_num] = results
        all_issues.extend([(prompt_num, issue) for issue in issues])
        all_stats['successful_prompts'] += 1
        
        # Aggregate statistics
        all_stats['total_cells'] += stats['total_cells']
        all_stats['english_cells'] += stats['english_cells']
        all_stats['non_english_cells'] += stats['non_english_cells']
        
        # Track missing languages
        for lang in stats['missing_languages']:
            all_stats['missing_languages_count'][lang] = all_stats['missing_languages_count'].get(lang, 0) + 1
            # Track which prompts are missing this language
            if lang not in all_stats['missing_languages_prompts']:
                all_stats['missing_languages_prompts'][lang] = []
            all_stats['missing_languages_prompts'][lang].append(prompt_num)
        
        # Aggregate by element
        for elem_type in ELEMENT_TYPES:
            all_stats['by_element'][elem_type]['english'] += stats['by_element'][elem_type]['english']
            all_stats['by_element'][elem_type]['non_english'] += stats['by_element'][elem_type]['non_english']
        
        # Store prompt details
        all_stats['prompt_details'][prompt_num] = {
            'total_cells': stats['total_cells'],
            'english_cells': stats['english_cells'],
            'non_english_cells': stats['non_english_cells'],
            'missing_languages': stats['missing_languages']
        }
    
    return {
        'results': all_results,
        'issues': all_issues,
        'statistics': all_stats
    }


def print_verification_report(verification_data: Dict):
    """Print a comprehensive verification report."""
    stats = verification_data['statistics']
    issues = verification_data['issues']
    
    print("\n" + "="*80)
    print("VERIFICATION REPORT")
    print("="*80)
    
    # Overall statistics
    print(f"\n[STATISTICS] OVERALL STATISTICS:")
    print(f"  Total prompts found: {stats['total_prompts']}")
    print(f"  Successfully verified: {stats['successful_prompts']}")
    print(f"  Failed: {stats['failed_prompts']}")
    print(f"  Total cells: {stats['total_cells']:,}")
    print(f"  English cells: {stats['english_cells']:,} ({100*stats['english_cells']/stats['total_cells']:.2f}%)")
    print(f"  Non-English cells: {stats['non_english_cells']:,} ({100*stats['non_english_cells']/stats['total_cells']:.2f}%)")
    
    # Statistics by element type
    print(f"\n[ELEMENTS] BY ELEMENT TYPE:")
    for elem_type in ELEMENT_TYPES:
        elem_stats = stats['by_element'][elem_type]
        total = elem_stats['english'] + elem_stats['non_english']
        if total > 0:
            pct_non_english = 100 * elem_stats['non_english'] / total
            print(f"  {elem_type:12s}: {elem_stats['non_english']:5d} non-English / {total:5d} total ({pct_non_english:5.2f}%)")
    
    # Missing languages
    if stats['missing_languages_count']:
        print(f"\n[WARNING] MISSING LANGUAGES (defaulted to English):")
        for lang_code, count in sorted(stats['missing_languages_count'].items(), key=lambda x: x[1], reverse=True):
            lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
            missing_prompts = stats.get('missing_languages_prompts', {}).get(lang_code, [])
            missing_prompts_sorted = sorted(missing_prompts)
            
            # Format prompt list (show all if <= 20, otherwise show first 20 + count)
            if len(missing_prompts_sorted) <= 20:
                prompts_str = ", ".join([f"{p}" for p in missing_prompts_sorted])
            else:
                prompts_str = ", ".join([f"{p}" for p in missing_prompts_sorted[:20]]) + f" ... and {len(missing_prompts_sorted) - 20} more"
            
            print(f"  {lang_name:15s} ({lang_code:5s}): missing in {count:3d} prompts")
            print(f"    Prompts: {prompts_str}")
    
    # Non-English cases summary
    print(f"\n[NON-ENGLISH] NON-ENGLISH CASES FOUND: {len(issues):,}")
    if issues:
        # Group by element type
        by_element = {}
        for prompt_num, issue in issues:
            elem = issue['element']
            if elem not in by_element:
                by_element[elem] = []
            by_element[elem].append((prompt_num, issue))
        
        print(f"\n  Breakdown by element type:")
        for elem_type in ELEMENT_TYPES:
            if elem_type in by_element:
                count = len(by_element[elem_type])
                print(f"    {elem_type:12s}: {count:4d} cases")
        
        # Show sample cases
        print(f"\n  Sample cases (first 10):")
        for i, (prompt_num, issue) in enumerate(issues[:10]):
            lang_name = LANG_CODE_TO_NAME.get(issue['language'], issue['language'])
            scripts_str = ", ".join([f"{k}({v})" for k, v in issue['scripts'].items()])
            print(f"    Prompt {prompt_num:3d} | {lang_name:15s} | {issue['element']:12s} | {scripts_str}")
    
    # Prompt-level summary
    print(f"\n[PROMPTS] PROMPT-LEVEL SUMMARY:")
    print(f"  Prompts with most non-English content:")
    prompt_non_english = []
    for prompt_num, details in stats['prompt_details'].items():
        if details['non_english_cells'] > 0:
            prompt_non_english.append((prompt_num, details['non_english_cells'], details['total_cells']))
    
    prompt_non_english.sort(key=lambda x: x[1], reverse=True)
    for prompt_num, non_eng, total in prompt_non_english[:10]:
        pct = 100 * non_eng / total
        print(f"    Prompt {prompt_num:3d}: {non_eng:3d}/{total:3d} non-English ({pct:5.2f}%)")
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)


def verify_specific_cases():
    """Verify specific known cases to ensure correctness."""
    print("\n" + "="*80)
    print("SPECIFIC CASE VERIFICATION")
    print("="*80)
    
    # Test case 1: Prompt 1, Japanese, Literals
    print("\n✓ Test Case 1: Prompt 1, Japanese, Literals")
    results, _, _ = verify_prompt(1)
    if results and 'ja' in results:
        value = results['ja']['literals']
        expected = 0.0  # Should be non-English (has Japanese script)
        status = "✓ CORRECT" if value == expected else f"✗ INCORRECT (expected {expected}, got {value})"
        print(f"  Value: {value} | Expected: {expected} | {status}")
    
    # Test case 2: Prompt 1, Japanese, Comments
    print("\n✓ Test Case 2: Prompt 1, Japanese, Comments")
    if results and 'ja' in results:
        value = results['ja']['comments']
        expected = 0.0  # Should be non-English (has Japanese script)
        status = "✓ CORRECT" if value == expected else f"✗ INCORRECT (expected {expected}, got {value})"
        print(f"  Value: {value} | Expected: {expected} | {status}")
    
    # Test case 3: Prompt 1, Japanese, Variables
    print("\n✓ Test Case 3: Prompt 1, Japanese, Variables")
    if results and 'ja' in results:
        value = results['ja']['variables']
        expected = 1.0  # Should be English (only English/ASCII)
        status = "✓ CORRECT" if value == expected else f"✗ INCORRECT (expected {expected}, got {value})"
        print(f"  Value: {value} | Expected: {expected} | {status}")
    
    # Test case 4: Prompt 1, Chinese, Docstrings
    print("\n✓ Test Case 4: Prompt 1, Chinese, Docstrings")
    if results and 'zh-CN' in results:
        value = results['zh-CN']['docstrings']
        expected = 0.0  # Should be non-English (has CJK Unified Ideographs)
        status = "✓ CORRECT" if value == expected else f"✗ INCORRECT (expected {expected}, got {value})"
        print(f"  Value: {value} | Expected: {expected} | {status}")


def main():
    """Main entry point."""
    # Verify all prompts
    verification_data = verify_all_prompts(data_dir="data", max_prompts=150)
    
    # Print comprehensive report
    print_verification_report(verification_data)
    
    # Verify specific cases
    verify_specific_cases()
    
    # Save detailed results to file
    output_file = "data/heatmap_verification_report.json"
    try:
        # Convert to JSON-serializable format
        stats = verification_data['statistics']
        report = {
            'statistics': {
                'total_prompts': stats['total_prompts'],
                'successful_prompts': stats['successful_prompts'],
                'failed_prompts': stats['failed_prompts'],
                'total_cells': stats['total_cells'],
                'english_cells': stats['english_cells'],
                'non_english_cells': stats['non_english_cells'],
                'missing_languages': {
                    lang_code: {
                        'count': stats['missing_languages_count'][lang_code],
                        'prompts': sorted(stats.get('missing_languages_prompts', {}).get(lang_code, []))
                    }
                    for lang_code in stats['missing_languages_count'].keys()
                },
                'by_element': stats['by_element']
            },
            'total_issues': len(verification_data['issues']),
            'sample_issues': verification_data['issues'][:50]  # First 50 issues
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Detailed report saved to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")


if __name__ == "__main__":
    main()