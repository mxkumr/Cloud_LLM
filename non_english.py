import os
import sys
import json
import re
from collections import defaultdict
from typing import Dict, Any, List, Optional

import matplotlib.pyplot as plt


def ensure_mlp_on_path(project_root: str) -> str:
    mlp_dir = os.path.join(project_root, "Multi_language_parser")
    if mlp_dir not in sys.path:
        sys.path.insert(0, mlp_dir)
    return mlp_dir


def is_likely_programming_term(text: str, source_code: Optional[str] = None) -> bool:
    """
    Check if a word is likely a programming term (English command/method).
    Returns True if:
    1. The word appears after a '.' in source code (e.g., "obj.method", ".method")
    2. The word is a common programming term
    """
    text_lower = text.strip().lower()
    
    # Common programming terms that should be classified as English
    common_programming_terms = {
        # Method names
        'cast', 'seek', 'read', 'write', 'join', 'split', 'strip', 'replace',
        'append', 'extend', 'insert', 'remove', 'pop', 'clear', 'copy',
        'get', 'set', 'add', 'update', 'delete', 'find', 'search', 'filter',
        'map', 'reduce', 'sort', 'reverse', 'index', 'count', 'len',
        'start', 'stop', 'begin', 'end', 'init', 'initialize',
        # Class/type names
        'bytesio', 'stringio', 'file', 'buffer', 'stream', 'reader', 'writer',
        # Common identifiers
        'buffer', 'source', 'destination', 'dest', 'src', 'ptr', 'pointer',
        'num_bytes', 'byte_count', 'size', 'length', 'offset',
    }
    
    if text_lower in common_programming_terms:
        return True
    
    # Check if word appears after '.' in source code
    if source_code:
        # Pattern: word appears after '.' without space (e.g., ".word", "obj.word", "module.word")
        # Matches patterns like:
        # - "obj.word(" (method call)
        # - "obj.word[" (attribute access with bracket)
        # - "obj.word." (chained attribute access)
        # - "obj.word " (attribute access followed by space)
        # - "obj.word\n" (attribute access at end of line)
        # Case-insensitive matching
        escaped_text = re.escape(text)
        # Match word after dot, followed by optional whitespace and then one of: ( [ . space end-of-line
        pattern = r'\.' + escaped_text + r'(?:\s*[\(\[\.]|\s|$)'
        if re.search(pattern, source_code, re.IGNORECASE):
            return True
    
    return False


def classify_text(text: str, source_code: Optional[str] = None) -> str:
    """
    Return script label using Multi_language_parser.language_detection.classify_string.
    If the text is likely a programming term (appears after '.' or is a common term),
    classify it as English/ASCII.
    """
    # Check if it's likely a programming term first
    if is_likely_programming_term(text, source_code):
        return "English/ASCII"
    
    try:
        from language_detection import classify_string  # type: ignore
        return classify_string(text).get("script", "Unknown")
    except Exception:
        # Fallback: simple ASCII check
        try:
            text.encode("ascii")
            return "English/ASCII"
        except Exception:
            return "Non-English"


def aggregate_counts(elements: Dict[str, List[str]], file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Aggregate counts of elements by language/script.
    If file_path is provided, reads the source code to check if identifiers
    appear after '.' (indicating method/attribute access, likely English).
    """
    categories = [
        "identifiers",
        "literals",
        "comments",
        "docstrings",
        "functions",
        "classes",
    ]

    # Try to read source code if file_path is provided
    source_code = None
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source_code = f.read()
        except Exception:
            # If we can't read the file, continue without source code context
            pass

    # Track both counts and instances
    overall = defaultdict(lambda: {"count": 0, "instances": []})
    by_category = {cat: defaultdict(lambda: {"count": 0, "instances": []}) for cat in categories}

    for cat in categories:
        values = elements.get(cat, []) or []
        for value in values:
            value_str = str(value)
            # Pass source_code to classify_text to check for '.' patterns
            script = classify_text(value_str, source_code)
            # Normalize to two buckets for overview; keep script names for detail
            bucket = "English/ASCII" if script == "English/ASCII" else script or "Non-English"
            
            # Update overall
            overall[bucket]["count"] += 1
            overall[bucket]["instances"].append(value_str)
            
            # Update by category
            by_category[cat][bucket]["count"] += 1
            by_category[cat][bucket]["instances"].append(value_str)

    # Convert defaultdicts to regular dicts
    return {
        "overall": {k: {"count": v["count"], "instances": v["instances"]} for k, v in overall.items()},
        "by_category": {k: {script: {"count": data["count"], "instances": data["instances"]} 
                            for script, data in v.items()} 
                        for k, v in by_category.items()},
    }


def plot_overall_pie(counts: Dict[str, Any], out_path: str, title: str) -> None:
    if not counts:
        return
    
    # Handle both old format (int) and new format (dict with count)
    def get_count(value):
        if isinstance(value, dict):
            return value.get("count", 0)
        return int(value)
    
    labels = list(counts.keys())
    values = [get_count(counts[k]) for k in labels]
    
    # Create labels with both count and percentage
    def make_autopct(values):
        def autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val})'
        return autopct
    
    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=labels, autopct=make_autopct(values), startangle=90)
    plt.axis("equal")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_category_bars(by_category: Dict[str, Dict[str, Any]], out_path: str, title: str) -> None:
    categories = list(by_category.keys())
    # Collect all bucket names across categories
    all_buckets = sorted({b for v in by_category.values() for b in v.keys()}) or ["English/ASCII", "Non-English"]

    # Helper to extract count from old or new format
    def get_count(category_data, bucket):
        bucket_data = category_data.get(bucket, 0)
        if isinstance(bucket_data, dict):
            return bucket_data.get("count", 0)
        return int(bucket_data)

    import numpy as np
    x = np.arange(len(categories))
    width = 0.8 / max(1, len(all_buckets))

    plt.figure(figsize=(14, 8))
    bars = []
    for i, bucket in enumerate(all_buckets):
        vals = [get_count(by_category.get(cat, {}), bucket) for cat in categories]
        bar = plt.bar(x + i * width - (len(all_buckets)-1) * width / 2, vals, width=width, label=bucket)
        bars.append(bar)
        
        # Add count labels on top of bars
        for j, (bar_rect, val) in enumerate(zip(bar, vals)):
            if val > 0:  # Only show label if there's a value
                plt.text(bar_rect.get_x() + bar_rect.get_width()/2., bar_rect.get_height() + 0.1,
                        f'{val}', ha='center', va='bottom', fontsize=8)

    plt.xticks(x, categories, rotation=30, ha="right")
    plt.ylabel("Count")
    plt.title(title)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def create_totals_summary(summary: Dict[str, Any]) -> str:
    """Create a summary table with total counts per language."""
    lines = []
    lines.append("=" * 100)
    lines.append("LANGUAGE TOTALS SUMMARY")
    lines.append("=" * 100)
    
    # Helper to extract count
    def get_count(value):
        if isinstance(value, dict):
            return value.get("count", 0)
        return int(value)
    
    # Collect all categories
    all_categories = set()
    for data in summary.values():
        by_category = data.get("by_category", {})
        all_categories.update(by_category.keys())
    all_categories = sorted(list(all_categories))
    
    # Header
    header = f"{'Language':<15} {'Total':<12} {'English/ASCII':<15} {'Non-English':<15}"
    for cat in all_categories:
        header += f" {cat.title():<15}"
    lines.append(header)
    lines.append("-" * 100)
    
    # Calculate totals for each language
    language_totals = []
    for lang_key, data in sorted(summary.items()):
        overall = data.get("overall", {})
        by_category = data.get("by_category", {})
        
        # Total count
        total_count = sum(get_count(v) for v in overall.values())
        
        # English/ASCII and Non-English counts
        english_count = get_count(overall.get("English/ASCII", 0))
        non_english_count = total_count - english_count
        
        # Category totals
        category_totals = {}
        for cat in all_categories:
            cat_data = by_category.get(cat, {})
            category_totals[cat] = sum(get_count(v) for v in cat_data.values())
        
        language_totals.append({
            "language": lang_key,
            "total": total_count,
            "english": english_count,
            "non_english": non_english_count,
            "categories": category_totals
        })
    
    # Sort by total count (descending)
    language_totals.sort(key=lambda x: x["total"], reverse=True)
    
    # Print rows
    for item in language_totals:
        row = f"{item['language']:<15} {item['total']:<12} {item['english']:<15} {item['non_english']:<15}"
        for cat in all_categories:
            row += f" {item['categories'].get(cat, 0):<15}"
        lines.append(row)
    
    # Add grand totals row
    grand_total = sum(item["total"] for item in language_totals)
    grand_english = sum(item["english"] for item in language_totals)
    grand_non_english = sum(item["non_english"] for item in language_totals)
    grand_categories = {}
    for cat in all_categories:
        grand_categories[cat] = sum(item["categories"].get(cat, 0) for item in language_totals)
    
    lines.append("-" * 100)
    totals_row = f"{'TOTAL':<15} {grand_total:<12} {grand_english:<15} {grand_non_english:<15}"
    for cat in all_categories:
        totals_row += f" {grand_categories[cat]:<15}"
    lines.append(totals_row)
    
    lines.append("=" * 100)
    return "\n".join(lines)


def create_detailed_summary_table(summary: Dict[str, Any]) -> str:
    """Create a detailed text summary table of the language analysis."""
    lines = []
    lines.append("=" * 80)
    lines.append("DETAILED LANGUAGE ANALYSIS SUMMARY")
    lines.append("=" * 80)
    
    for lang_key, data in summary.items():
        lines.append(f"\n[LANGUAGE] {lang_key.upper()}")
        lines.append("-" * 40)
        
        # Overall summary
        overall = data.get("overall", {})
        
        # Helper to extract count
        def get_count(value):
            if isinstance(value, dict):
                return value.get("count", 0)
            return int(value)
        
        total_items = sum(get_count(v) for v in overall.values())
        lines.append(f"Total Items: {total_items}")
        
        # Sort by count
        overall_items = [(script, get_count(count_data)) for script, count_data in overall.items()]
        overall_items.sort(key=lambda x: x[1], reverse=True)
        
        for script, count in overall_items:
            percentage = (count / total_items * 100) if total_items > 0 else 0
            lines.append(f"  {script}: {count} items ({percentage:.1f}%)")
        
        # Category breakdown
        lines.append(f"\n[CATEGORY BREAKDOWN]:")
        by_category = data.get("by_category", {})
        for category, scripts in by_category.items():
            if scripts:  # Only show categories with data
                lines.append(f"  {category.title()}:")
                # Sort by count
                script_items = [(script, get_count(count_data)) for script, count_data in scripts.items()]
                script_items.sort(key=lambda x: x[1], reverse=True)
                for script, count in script_items:
                    lines.append(f"    {script}: {count}")
    
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def run_visualization(input_path: str, charts_dir: str, summary_out: Optional[str] = None) -> None:
    os.makedirs(charts_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        parsed = json.load(f)

    results = parsed.get("results", {}) if isinstance(parsed, dict) else {}
    summary: Dict[str, Any] = {}

    print(f"Processing {len(results)} languages...")
    
    for lang_key, item in results.items():
        if not item or not item.get("success"):
            print(f"Skipping {lang_key} (no successful parsing)")
            continue
            
        print(f"Processing {lang_key}...")
        elements = item.get("elements", {}) or {}
        file_path = item.get("file_path")
        counts = aggregate_counts(elements, file_path)
        summary[lang_key] = counts

        # Charts per language
        pie_path = os.path.join(charts_dir, f"{lang_key}_overall_pie.png")
        plot_overall_pie(counts["overall"], pie_path, f"Overall Script Distribution: {lang_key}")

        bars_path = os.path.join(charts_dir, f"{lang_key}_by_category.png")
        plot_category_bars(counts["by_category"], bars_path, f"Script Distribution by Category: {lang_key}")

    # Create overall comparison chart
    if summary:
        create_overall_comparison_chart(summary, charts_dir)

    # Create totals summary
    totals_summary = create_totals_summary(summary)
    print("\n" + totals_summary)

    # Create detailed summary
    detailed_summary = create_detailed_summary_table(summary)
    print("\n" + detailed_summary)

    # Save summary JSON with enhanced data
    if summary_out:
        enhanced_summary = {
            "summary": summary,
            "totals_summary": totals_summary,
            "detailed_analysis": detailed_summary,
            "total_languages": len(summary),
            "generated_at": __import__('datetime').datetime.now().isoformat()
        }
        with open(summary_out, "w", encoding="utf-8") as f:
            json.dump(enhanced_summary, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Saved charts to: {charts_dir}")
    if summary_out:
        print(f"[SUCCESS] Saved enhanced summary to: {summary_out}")


def create_overall_comparison_chart(summary: Dict[str, Any], charts_dir: str) -> None:
    """Create an overall comparison chart across all languages."""
    import numpy as np
    
    languages = list(summary.keys())
    all_scripts = set()
    
    # Collect all unique scripts
    for data in summary.values():
        overall = data.get("overall", {})
        all_scripts.update(overall.keys())
    
    all_scripts = sorted(list(all_scripts))
    
    # Helper to extract count
    def get_count(overall_data, script):
        script_data = overall_data.get(script, 0)
        if isinstance(script_data, dict):
            return script_data.get("count", 0)
        return int(script_data)
    
    # Create data matrix
    data_matrix = []
    for lang in languages:
        overall = summary[lang].get("overall", {})
        row = [get_count(overall, script) for script in all_scripts]
        data_matrix.append(row)
    
    data_matrix = np.array(data_matrix)
    
    # Create stacked bar chart
    plt.figure(figsize=(16, 10))
    x = np.arange(len(languages))
    width = 0.8
    
    bottom = np.zeros(len(languages))
    colors = plt.cm.Set3(np.linspace(0, 1, len(all_scripts)))
    
    for i, script in enumerate(all_scripts):
        values = data_matrix[:, i]
        if np.any(values > 0):  # Only plot if there are values
            plt.bar(x, values, width, bottom=bottom, label=script, color=colors[i])
            
            # Add count labels on bars
            for j, (val, bot) in enumerate(zip(values, bottom)):
                if val > 0:
                    plt.text(j, bot + val/2, f'{int(val)}', ha='center', va='center', 
                            fontsize=8, fontweight='bold')
            
            bottom += values
    
    plt.xlabel('Languages')
    plt.ylabel('Count')
    plt.title('Script Distribution Across All Languages')
    plt.xticks(x, languages, rotation=45, ha='right')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    comparison_path = os.path.join(charts_dir, "overall_comparison.png")
    plt.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"[SUCCESS] Created overall comparison chart: {comparison_path}")


def main() -> None:
    project_root = os.path.abspath(os.path.dirname(__file__))
    ensure_mlp_on_path(project_root)

    input_path = os.path.join(project_root, "data", "llm_parsed.json")
    charts_dir = os.path.join(project_root, "data", "language_charts")
    summary_out = os.path.join(project_root, "data", "non_english_summary.json")
    run_visualization(input_path, charts_dir, summary_out)


if __name__ == "__main__":
    main()



