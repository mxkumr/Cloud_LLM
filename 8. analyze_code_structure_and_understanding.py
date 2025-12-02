"""
Code Structure Statistics Script

Analyzes code structure metrics (length, syntax validity, execution success) 
to determine if the generated code works across different languages and prompts.

Usage:
    python 8. analyze_code_structure_and_understanding.py
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Language codes in order
LANGUAGE_CODES = ["en", "zh-CN", "hi", "es", "ar", "fr", "bn", "pt", "ru", "id", "ur", "de", "ja", "mr", "vi", "te", "ha", "tr"]

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


def analyze_prompt(prompt_num: int, data_dir: str = "data") -> Tuple[Optional[Dict], Dict]:
    """
    Analyze code structure for a single prompt.
    
    Returns:
        (results_dict, statistics_dict)
        - results_dict: {language: {structure_metrics}}
        - statistics_dict: aggregated stats for this prompt
    """
    prompt_dir = os.path.join(data_dir, f"prompt_{prompt_num}")
    validation_path = os.path.join(prompt_dir, "code_validation.json")
    
    if not os.path.exists(validation_path):
        return None, {}
    
    try:
        with open(validation_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        detailed_results = data.get('detailed_results', {})
        summary = data.get('summary', {})
        
        results = {}
        stats = {
            'total_languages': len(LANGUAGE_CODES),
            'syntax_valid': 0,
            'syntax_errors': 0,
            'execution_success': 0,
            'execution_errors': 0,
            'total_code_length': 0,
            'total_execution_time': 0,
            'by_language': {lang: {
                'syntax_valid': 0,
                'syntax_errors': 0,
                'execution_success': 0,
                'execution_errors': 0,
                'code_lengths': [],
                'execution_times': []
            } for lang in LANGUAGE_CODES}
        }
        
        for lang_code in LANGUAGE_CODES:
            lang_data = detailed_results.get(lang_code)
            results[lang_code] = {
                'structure': {}
            }
            
            if not lang_data:
                # Missing language - all zeros
                continue
            
            # Code structure metrics
            syntax_info = lang_data.get('syntax', {})
            execution_info = lang_data.get('execution', {})
            code_length = lang_data.get('code_length', 0)
            
            syntax_valid = syntax_info.get('valid', False)
            execution_success = execution_info.get('success', False)
            execution_time = execution_info.get('execution_time', 0)
            
            results[lang_code]['structure'] = {
                'code_length': code_length,
                'syntax_valid': syntax_valid,
                'syntax_error_type': syntax_info.get('error_type'),
                'syntax_error_message': syntax_info.get('error_message'),
                'execution_success': execution_success,
                'execution_error_type': execution_info.get('error_type'),
                'execution_error_message': execution_info.get('error_message'),
                'execution_time': execution_time
            }
            
            # Update statistics
            if syntax_valid:
                stats['syntax_valid'] += 1
                stats['by_language'][lang_code]['syntax_valid'] += 1
            else:
                stats['syntax_errors'] += 1
                stats['by_language'][lang_code]['syntax_errors'] += 1
            
            if execution_success:
                stats['execution_success'] += 1
                stats['by_language'][lang_code]['execution_success'] += 1
                if execution_time > 0:
                    stats['total_execution_time'] += execution_time
                    stats['by_language'][lang_code]['execution_times'].append(execution_time)
            else:
                stats['execution_errors'] += 1
                stats['by_language'][lang_code]['execution_errors'] += 1
            
            stats['total_code_length'] += code_length
            stats['by_language'][lang_code]['code_lengths'].append(code_length)
        
        # Calculate averages
        total_analyzed = stats['syntax_valid'] + stats['syntax_errors']
        if total_analyzed > 0:
            stats['avg_code_length'] = stats['total_code_length'] / total_analyzed
            stats['syntax_valid_rate'] = stats['syntax_valid'] / total_analyzed
            stats['execution_success_rate'] = stats['execution_success'] / total_analyzed if total_analyzed > 0 else 0
        
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
    print("CODE STRUCTURE STATISTICS")
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
            'total_analyzed': 0,
            'syntax_valid_count': 0,
            'syntax_error_count': 0,
            'execution_success_count': 0,
            'execution_error_count': 0,
            'code_lengths': [],
            'execution_times': [],
            'syntax_error_prompts': [],
            'execution_error_prompts': []
        } for lang in LANGUAGE_CODES},
        'by_prompt': {}
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
        
        # Store prompt-level stats
        all_stats['by_prompt'][prompt_num] = {
            'syntax_valid_rate': stats.get('syntax_valid_rate', 0),
            'execution_success_rate': stats.get('execution_success_rate', 0),
            'avg_code_length': stats.get('avg_code_length', 0)
        }
        
        # Aggregate statistics by language
        for lang_code in LANGUAGE_CODES:
            lang_results = results.get(lang_code, {})
            if not lang_results:
                continue
            
            structure = lang_results.get('structure', {})
            
            all_stats['by_language'][lang_code]['total_analyzed'] += 1
            
            if structure.get('syntax_valid', False):
                all_stats['by_language'][lang_code]['syntax_valid_count'] += 1
            else:
                all_stats['by_language'][lang_code]['syntax_error_count'] += 1
                all_stats['by_language'][lang_code]['syntax_error_prompts'].append(prompt_num)
            
            if structure.get('execution_success', False):
                all_stats['by_language'][lang_code]['execution_success_count'] += 1
                exec_time = structure.get('execution_time', 0)
                if exec_time > 0:
                    all_stats['by_language'][lang_code]['execution_times'].append(exec_time)
            else:
                all_stats['by_language'][lang_code]['execution_error_count'] += 1
                all_stats['by_language'][lang_code]['execution_error_prompts'].append(prompt_num)
            
            code_len = structure.get('code_length', 0)
            if code_len > 0:
                all_stats['by_language'][lang_code]['code_lengths'].append(code_len)
    
    return {
        'results': all_results,
        'statistics': all_stats
    }


def print_statistics_report(analysis_data: Dict):
    """Print a comprehensive statistics report."""
    stats = analysis_data['statistics']
    
    print("\n" + "="*80)
    print("CODE STRUCTURE REPORT")
    print("="*80)
    
    # Overall statistics
    print(f"\n[OVERALL] SUMMARY:")
    print(f"  Total prompts analyzed: {stats['successful_prompts']}")
    print(f"  Failed prompts: {stats['failed_prompts']}")
    
    # Code structure statistics by language
    print(f"\n[CODE STRUCTURE] BY LANGUAGE:")
    print(f"\n{'Language':<20} {'Analyzed':<10} {'Syntax OK':<12} {'Syntax Err':<12} {'Exec OK':<10} {'Exec Err':<10} {'Avg Length':<12} {'Avg Time':<10}")
    print("-" * 110)
    
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
        
        if lang_stats['total_analyzed'] == 0:
            continue
        
        syntax_valid_rate = lang_stats['syntax_valid_count'] / lang_stats['total_analyzed'] if lang_stats['total_analyzed'] > 0 else 0
        exec_success_rate = lang_stats['execution_success_count'] / lang_stats['total_analyzed'] if lang_stats['total_analyzed'] > 0 else 0
        avg_length = np.mean(lang_stats['code_lengths']) if lang_stats['code_lengths'] else 0
        avg_time = np.mean(lang_stats['execution_times']) if lang_stats['execution_times'] else 0
        
        print(f"{lang_name:<20} {lang_stats['total_analyzed']:<10} "
              f"{lang_stats['syntax_valid_count']:<12} {lang_stats['syntax_error_count']:<12} "
              f"{lang_stats['execution_success_count']:<10} {lang_stats['execution_error_count']:<10} "
              f"{avg_length:<12.0f} {avg_time:<10.4f}")
    
    # Detailed statistics by language
    print(f"\n[BY LANGUAGE] DETAILED STATISTICS:")
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
        
        if lang_stats['total_analyzed'] == 0:
            continue
        
        print(f"\n  {lang_name} ({lang_code}):")
        print(f"    Total analyzed: {lang_stats['total_analyzed']}")
        
        # Syntax statistics
        syntax_rate = lang_stats['syntax_valid_count'] / lang_stats['total_analyzed'] * 100 if lang_stats['total_analyzed'] > 0 else 0
        print(f"    Syntax: {lang_stats['syntax_valid_count']} valid, {lang_stats['syntax_error_count']} errors ({syntax_rate:.1f}% valid)")
        if lang_stats['syntax_error_prompts']:
            error_prompts_str = ', '.join([f"prompt_{p}" for p in sorted(lang_stats['syntax_error_prompts'])])
            print(f"      Syntax errors in: {error_prompts_str}")
        
        # Execution statistics
        exec_rate = lang_stats['execution_success_count'] / lang_stats['total_analyzed'] * 100 if lang_stats['total_analyzed'] > 0 else 0
        if lang_stats['execution_times']:
            avg_time = np.mean(lang_stats['execution_times'])
            min_time = min(lang_stats['execution_times'])
            max_time = max(lang_stats['execution_times'])
            print(f"    Execution: {lang_stats['execution_success_count']} success, {lang_stats['execution_error_count']} errors ({exec_rate:.1f}% success)")
            print(f"      Execution time: Avg={avg_time:.4f}s, Min={min_time:.4f}s, Max={max_time:.4f}s")
        else:
            print(f"    Execution: {lang_stats['execution_success_count']} success, {lang_stats['execution_error_count']} errors ({exec_rate:.1f}% success)")
        if lang_stats['execution_error_prompts']:
            error_prompts_str = ', '.join([f"prompt_{p}" for p in sorted(lang_stats['execution_error_prompts'])])
            print(f"      Execution errors in: {error_prompts_str}")
        
        # Code length statistics
        if lang_stats['code_lengths']:
            avg_len = np.mean(lang_stats['code_lengths'])
            min_len = min(lang_stats['code_lengths'])
            max_len = max(lang_stats['code_lengths'])
            print(f"    Code length: Avg={avg_len:.0f}, Min={min_len:.0f}, Max={max_len:.0f}")
    
    # Prompt-level summary
    print(f"\n[PROMPTS] PROMPT-LEVEL SUMMARY:")
    print(f"  Prompts with best syntax validity rates:")
    prompt_syntax = [(p, s['syntax_valid_rate']) for p, s in stats['by_prompt'].items()]
    prompt_syntax.sort(key=lambda x: x[1], reverse=True)
    for prompt_num, rate in prompt_syntax[:10]:
        print(f"    Prompt {prompt_num:3d}: {rate*100:5.1f}% valid syntax")
    
    print(f"\n  Prompts with worst syntax validity rates:")
    for prompt_num, rate in prompt_syntax[-10:]:
        print(f"    Prompt {prompt_num:3d}: {rate*100:5.1f}% valid syntax")
    
    print(f"\n  Prompts with best execution success rates:")
    prompt_exec = [(p, s['execution_success_rate']) for p, s in stats['by_prompt'].items()]
    prompt_exec.sort(key=lambda x: x[1], reverse=True)
    for prompt_num, rate in prompt_exec[:10]:
        print(f"    Prompt {prompt_num:3d}: {rate*100:5.1f}% execution success")
    
    print(f"\n  Prompts with worst execution success rates:")
    for prompt_num, rate in prompt_exec[-10:]:
        print(f"    Prompt {prompt_num:3d}: {rate*100:5.1f}% execution success")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


def save_detailed_report(analysis_data: Dict, output_file: str = "data/code_structure_report.json"):
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
        'by_prompt': {}
    }
    
    # Language statistics
    for lang_code in LANGUAGE_CODES:
        lang_stats = stats['by_language'][lang_code]
        if lang_stats['total_analyzed'] > 0:
            lang_name = LANG_CODE_TO_NAME.get(lang_code, lang_code)
            report['by_language'][lang_code] = {
                'name': lang_name,
                'total_analyzed': lang_stats['total_analyzed'],
                'syntax': {
                    'valid_count': lang_stats['syntax_valid_count'],
                    'error_count': lang_stats['syntax_error_count'],
                    'valid_rate': lang_stats['syntax_valid_count'] / lang_stats['total_analyzed'] if lang_stats['total_analyzed'] > 0 else 0,
                    'error_prompts': sorted(lang_stats['syntax_error_prompts'])
                },
                'execution': {
                    'success_count': lang_stats['execution_success_count'],
                    'error_count': lang_stats['execution_error_count'],
                    'success_rate': lang_stats['execution_success_count'] / lang_stats['total_analyzed'] if lang_stats['total_analyzed'] > 0 else 0,
                    'avg_time': float(np.mean(lang_stats['execution_times'])) if lang_stats['execution_times'] else 0,
                    'min_time': float(min(lang_stats['execution_times'])) if lang_stats['execution_times'] else 0,
                    'max_time': float(max(lang_stats['execution_times'])) if lang_stats['execution_times'] else 0,
                    'error_prompts': sorted(lang_stats['execution_error_prompts'])
                },
                'code_length': {
                    'avg': float(np.mean(lang_stats['code_lengths'])) if lang_stats['code_lengths'] else 0,
                    'min': float(min(lang_stats['code_lengths'])) if lang_stats['code_lengths'] else 0,
                    'max': float(max(lang_stats['code_lengths'])) if lang_stats['code_lengths'] else 0
                }
            }
    
    # Prompt statistics
    for prompt_num, prompt_stats in stats['by_prompt'].items():
        report['by_prompt'][prompt_num] = {
            'syntax_valid_rate': prompt_stats['syntax_valid_rate'],
            'execution_success_rate': prompt_stats['execution_success_rate'],
            'avg_code_length': prompt_stats['avg_code_length']
        }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n[SUCCESS] Detailed report saved to: {output_file}")
    except Exception as e:
        print(f"\n[WARNING] Could not save report: {e}")


def create_heatmap_visualization(analysis_data: Dict, output_path: str = "data/code_structure_heatmap.png"):
    """
    Create heatmap visualization for syntax and execution errors.
    
    Args:
        analysis_data: Dictionary with analysis results
        output_path: Path to save the heatmap figure
    """
    stats = analysis_data['statistics']
    results = analysis_data['results']
    
    # Find all prompt numbers
    prompt_numbers = sorted(results.keys())
    num_prompts = len(prompt_numbers)
    num_languages = len(LANGUAGE_CODES)
    
    # Create arrays for syntax and execution (1 = valid/success, 0 = error)
    syntax_data = np.ones((num_prompts, num_languages), dtype=np.float32)
    execution_data = np.ones((num_prompts, num_languages), dtype=np.float32)
    
    # Fill arrays with data
    for prompt_idx, prompt_num in enumerate(prompt_numbers):
        prompt_results = results[prompt_num]
        
        for lang_idx, lang_code in enumerate(LANGUAGE_CODES):
            lang_results = prompt_results.get(lang_code, {})
            
            if not lang_results:
                # Missing data - mark as error (0)
                syntax_data[prompt_idx, lang_idx] = 0.0
                execution_data[prompt_idx, lang_idx] = 0.0
                continue
            
            structure = lang_results.get('structure', {})
            
            # Syntax: 1 = valid, 0 = error
            syntax_data[prompt_idx, lang_idx] = 1.0 if structure.get('syntax_valid', False) else 0.0
            
            # Execution: 1 = success, 0 = error
            execution_data[prompt_idx, lang_idx] = 1.0 if structure.get('execution_success', False) else 0.0
    
    # Create figure with 1×2 subplot grid (side by side)
    fig, axes = plt.subplots(1, 2, figsize=(24, 10))
    fig.suptitle('Code Structure Analysis: Syntax Validity and Execution Success',
                 fontsize=16, fontweight='bold', y=0.98)
    
    # Language names for x-axis
    lang_labels = [LANG_CODE_TO_NAME.get(code, code) for code in LANGUAGE_CODES]
    
    # Create syntax heatmap
    ax1 = axes[0]
    im1 = ax1.imshow(syntax_data, aspect='auto', cmap='RdYlGn', 
                     vmin=0, vmax=1, interpolation='nearest')
    ax1.set_title('Syntax Validity', fontsize=14, fontweight='bold', pad=10)
    ax1.set_xticks(np.arange(num_languages))
    ax1.set_xticklabels(lang_labels, rotation=45, ha='right', fontsize=9)
    ax1.set_xlabel('Languages', fontsize=11, fontweight='bold')
    
    # Set y-axis labels (prompts)
    if num_prompts <= 150:
        step = max(1, num_prompts // 20)
        y_ticks = np.arange(0, num_prompts, step)
        y_labels = [f"{prompt_numbers[i]}" for i in y_ticks]
        ax1.set_yticks(y_ticks)
        ax1.set_yticklabels(y_labels, fontsize=8)
    else:
        step = max(1, num_prompts // 15)
        y_ticks = np.arange(0, num_prompts, step)
        y_labels = [f"{prompt_numbers[i]}" for i in y_ticks]
        ax1.set_yticks(y_ticks)
        ax1.set_yticklabels(y_labels, fontsize=8)
    
    ax1.set_ylabel('Prompts', fontsize=11, fontweight='bold')
    
    # Add colorbar for syntax
    cbar1 = plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
    cbar1.set_label('Valid (1) / Error (0)', fontsize=10, rotation=270, labelpad=15)
    cbar1.set_ticks([0, 1])
    cbar1.set_ticklabels(['Error', 'Valid'])
    
    # Add grid for better readability
    ax1.set_xticks(np.arange(num_languages) - 0.5, minor=True)
    ax1.set_yticks(np.arange(num_prompts) - 0.5, minor=True)
    ax1.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Create execution heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(execution_data, aspect='auto', cmap='RdYlGn', 
                     vmin=0, vmax=1, interpolation='nearest')
    ax2.set_title('Execution Success', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xticks(np.arange(num_languages))
    ax2.set_xticklabels(lang_labels, rotation=45, ha='right', fontsize=9)
    ax2.set_xlabel('Languages', fontsize=11, fontweight='bold')
    
    # Set y-axis labels (prompts) - same as syntax
    if num_prompts <= 150:
        step = max(1, num_prompts // 20)
        y_ticks = np.arange(0, num_prompts, step)
        y_labels = [f"{prompt_numbers[i]}" for i in y_ticks]
        ax2.set_yticks(y_ticks)
        ax2.set_yticklabels(y_labels, fontsize=8)
    else:
        step = max(1, num_prompts // 15)
        y_ticks = np.arange(0, num_prompts, step)
        y_labels = [f"{prompt_numbers[i]}" for i in y_ticks]
        ax2.set_yticks(y_ticks)
        ax2.set_yticklabels(y_labels, fontsize=8)
    
    ax2.set_ylabel('Prompts', fontsize=11, fontweight='bold')
    
    # Add colorbar for execution
    cbar2 = plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)
    cbar2.set_label('Success (1) / Error (0)', fontsize=10, rotation=270, labelpad=15)
    cbar2.set_ticks([0, 1])
    cbar2.set_ticklabels(['Error', 'Success'])
    
    # Add grid for better readability
    ax2.set_xticks(np.arange(num_languages) - 0.5, minor=True)
    ax2.set_yticks(np.arange(num_prompts) - 0.5, minor=True)
    ax2.grid(which='minor', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n[SUCCESS] Heatmap visualization saved to: {output_path}")
    plt.close()


def main():
    """Main entry point."""
    # Analyze all prompts
    analysis_data = analyze_all_prompts(data_dir="data", max_prompts=150)
    
    # Print comprehensive report
    print_statistics_report(analysis_data)
    
    # Save detailed report
    save_detailed_report(analysis_data)
    
    # Create heatmap visualization
    create_heatmap_visualization(analysis_data)


if __name__ == "__main__":
    main()

