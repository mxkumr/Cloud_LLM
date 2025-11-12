"""
Prompt Language Influence Overview

This script scans each prompt folder inside the data directory, reads the
pre-parsed `llm_parsed.json` file, and generates an overall stacked bar chart
that compares English vs Non-English influence for every language-specific code
variant within that prompt. The chart and a JSON summary are saved back into
the prompt folder (`language_charts/` and `language_influence_summary.json`).

Usage:
    python prompt_language_influence.py
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


try:
    from non_english import aggregate_counts, ensure_mlp_on_path
except ImportError as exc:  # pragma: no cover - script level import guard
    raise ImportError(
        "Failed to import helper utilities from non_english.py. "
        "Ensure this script is executed from the project root."
    ) from exc


@dataclass
class LanguageInfluence:
    english: int
    non_english: int
    total: int
    scripts: Dict[str, int]

    @property
    def english_pct(self) -> float:
        return (self.english / self.total * 100) if self.total else 0.0

    @property
    def non_english_pct(self) -> float:
        return (self.non_english / self.total * 100) if self.total else 0.0


def ensure_project_paths() -> Tuple[str, str]:
    """Return project root and data directory, ensuring they exist."""
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(
            f"Data directory not found at {data_dir}. "
            "Run the parsing pipeline first to generate prompt folders."
        )
    ensure_mlp_on_path(project_root)
    return project_root, data_dir


def iter_prompt_folders(data_dir: str) -> Iterable[str]:
    """Yield absolute paths for prompt folders containing llm_parsed.json."""
    for entry in sorted(os.listdir(data_dir)):
        prompt_path = os.path.join(data_dir, entry)
        if not os.path.isdir(prompt_path):
            continue
        parsed_path = os.path.join(prompt_path, "llm_parsed.json")
        if os.path.isfile(parsed_path):
            yield prompt_path


def load_parsed_results(parsed_path: str) -> Dict[str, dict]:
    """Load parsed results for a prompt."""
    with open(parsed_path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected content in {parsed_path}: expected a dict.")
    return payload.get("results", {}) if isinstance(payload.get("results"), dict) else {}


def compute_influence_per_language(results: Dict[str, dict]) -> Dict[str, LanguageInfluence]:
    """Compute English vs Non-English influence per language entry."""
    influence: Dict[str, LanguageInfluence] = {}

    for lang_key, data in results.items():
        if not data or not data.get("success"):
            continue

        elements = data.get("elements", {}) or {}
        counts = aggregate_counts(elements)
        overall = counts.get("overall", {})

        english_count = int(overall.get("English/ASCII", 0))
        non_english_count = int(sum(val for script, val in overall.items() if script != "English/ASCII"))
        total = english_count + non_english_count

        influence[lang_key] = LanguageInfluence(
            english=english_count,
            non_english=non_english_count,
            total=total,
            scripts={script: int(val) for script, val in overall.items()},
        )

    return influence


def create_stacked_bar_chart(
    prompt_name: str,
    influence: Dict[str, LanguageInfluence],
    output_path: str,
) -> None:
    """Create and save a stacked bar chart showing English vs Non-English counts."""
    if not influence:
        return

    languages = list(influence.keys())
    english_counts = np.array([influence[lang].english for lang in languages], dtype=float)
    non_english_counts = np.array([influence[lang].non_english for lang in languages], dtype=float)

    plt.figure(figsize=(12, 7))
    x = np.arange(len(languages))
    bar_width = 0.65

    plt.bar(x, english_counts, bar_width, label="English/ASCII", color="#2ecc71")
    plt.bar(x, non_english_counts, bar_width, bottom=english_counts, label="Non-English", color="#e74c3c")

    for idx, lang in enumerate(languages):
        total = influence[lang].total
        english_val = english_counts[idx]
        non_english_val = non_english_counts[idx]
        if english_val > 0:
            plt.text(
                x[idx],
                english_val / 2,
                f"{int(english_val)}\n({influence[lang].english_pct:.1f}%)",
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold",
            )
        if non_english_val > 0:
            plt.text(
                x[idx],
                english_val + non_english_val / 2,
                f"{int(non_english_val)}\n({influence[lang].non_english_pct:.1f}%)",
                ha="center",
                va="center",
                fontsize=9,
                color="white",
                fontweight="bold",
            )
        if total == 0:
            plt.text(
                x[idx],
                0.05,
                "0",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    plt.xticks(x, languages, rotation=35, ha="right")
    plt.ylabel("Count")
    plt.title(f"English vs Non-English Influence per Language\n({prompt_name})")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def export_summary(
    prompt_dir: str,
    prompt_name: str,
    influence: Dict[str, LanguageInfluence],
) -> None:
    """Write a JSON summary capturing detailed influence metrics."""
    summary_out = os.path.join(prompt_dir, "language_influence_summary.json")

    overall_totals = {
        "english": int(sum(item.english for item in influence.values())),
        "non_english": int(sum(item.non_english for item in influence.values())),
    }
    overall_totals["total"] = overall_totals["english"] + overall_totals["non_english"]

    payload = {
        "prompt": prompt_name,
        "overall": overall_totals,
        "languages": {
            lang: {
                "english": item.english,
                "non_english": item.non_english,
                "total": item.total,
                "english_pct": round(item.english_pct, 2),
                "non_english_pct": round(item.non_english_pct, 2),
                "scripts": item.scripts,
            }
            for lang, item in influence.items()
        },
        "generated_at": __import__("datetime").datetime.now().isoformat(),
    }

    with open(summary_out, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def process_prompt_folder(prompt_dir: str) -> bool:
    """Process a single prompt folder and generate the influence chart."""
    prompt_name = os.path.basename(prompt_dir)
    parsed_path = os.path.join(prompt_dir, "llm_parsed.json")

    if not os.path.isfile(parsed_path):
        print(f"[SKIP] {prompt_name}: llm_parsed.json not found.")
        return False

    print(f"\n=== Processing {prompt_name} ===")
    try:
        results = load_parsed_results(parsed_path)
        influence = compute_influence_per_language(results)

        if not influence:
            print(f"[WARN] {prompt_name}: No successful language entries found.")
            return False

        charts_dir = os.path.join(prompt_dir, "language_charts")
        chart_path = os.path.join(charts_dir, "overall_english_vs_non_english.png")
        create_stacked_bar_chart(prompt_name, influence, chart_path)
        export_summary(prompt_dir, prompt_name, influence)

        print(f"[OK] Saved stacked bar chart to {chart_path}")
        print(f"[OK] Saved summary to {os.path.join(prompt_dir, 'language_influence_summary.json')}")
        return True
    except Exception as exc:  # pragma: no cover - runtime diagnostic
        print(f"[ERROR] Failed to process {prompt_name}: {exc}")
        return False


def main() -> None:
    try:
        _, data_dir = ensure_project_paths()
    except Exception as exc:
        print(f"[FATAL] {exc}")
        sys.exit(1)

    prompt_folders = list(iter_prompt_folders(data_dir))
    if not prompt_folders:
        print("[INFO] No prompt folders with llm_parsed.json found. Nothing to do.")
        return

    success = 0
    for prompt in prompt_folders:
        if process_prompt_folder(prompt):
            success += 1

    print(f"\nCompleted processing {success}/{len(prompt_folders)} prompt folder(s).")


if __name__ == "__main__":
    main()



