"""
Two-step Pipeline: Translation + LLM Generation (no parsing/visualization)

Usage:
    python pipeline_min.py prompts_input.json --model Qwen/Qwen3-30B-A3B-Instruct-2507
    python pipeline_min.py prompts_input.json  # Uses default model

This script mirrors the folder layout behavior of pipeline.py but stops after:
  1) Translating the base prompt into multiple languages
  2) Generating code with the LLM for each translated prompt

Outputs per prompt are saved to: data/<prompt_id>/{translated_prompts.json, llm_output.json}
"""

import os
import sys
import json
import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List


def ensure_dirs() -> str:
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)
    return project_root


def ensure_prompt_dir(data_dir: str, prompt_id: str) -> str:
    prompt_dir = os.path.join(data_dir, prompt_id)
    os.makedirs(prompt_dir, exist_ok=True)
    return prompt_dir


def load_prompts_from_json(json_file: str) -> List[Dict[str, str]]:
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'prompts' not in data:
            raise ValueError("JSON file must contain a 'prompts' key")

        prompts = []
        for prompt_data in data['prompts']:
            if not all(key in prompt_data for key in ['id', 'text']):
                raise ValueError("Each prompt must have 'id' and 'text' keys")
            prompts.append({
                'id': prompt_data['id'],
                'text': prompt_data['text']
            })

        return prompts
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file '{json_file}' not found")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")


def translate_prompt(prompt_text: str) -> Dict[str, Optional[str]]:
    from Prompt_translation import translate_prompt as pt_translate_prompt, TARGET_LANG_CODES

    try:
        return asyncio.run(pt_translate_prompt(prompt_text, TARGET_LANG_CODES))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(pt_translate_prompt(prompt_text, TARGET_LANG_CODES))


def setup_logger() -> None:
    logging.basicConfig(
        filename="data/llm_runtime.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s\t%(levelname)s\t%(message)s",
    )
    for noisy in ("httpx", "urllib3", "requests"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_llm_duration(language: str, start_ts: float, end_ts: float, seconds: float, success: bool = True, error_message: Optional[str] = None) -> None:
    start_iso = datetime.fromtimestamp(start_ts).isoformat(timespec="seconds")
    end_iso = datetime.fromtimestamp(end_ts).isoformat(timespec="seconds")
    minutes = seconds / 60.0
    if success:
        logging.info(
            f"lang={language}\tstart={start_iso}\tend={end_iso}\tduration_min={minutes:.3f}"
        )
    else:
        logging.error(
            f"lang={language}\tstart={start_iso}\tend={end_iso}\tduration_min={minutes:.3f}\terror={error_message}"
        )


def query_llm_for_translations(translations: Dict[str, str], model_name: str = None) -> Dict[str, str]:
    from LLMv2 import generate_code_with_retry
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch

    outputs: Dict[str, str] = {}

    model_name = model_name or "Qwen/Qwen3-30B-A3B-Instruct-2507"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )

    def query_func(prompt: str) -> str:
        return generate_code_with_retry(tokenizer, model, prompt, device)

    for lang, prompt in translations.items():
        if not prompt:
            outputs[lang] = None
            continue
        try:
            print(f"Querying transformers LLM for {lang}...")
            start_perf = time.perf_counter()
            start_wall = time.time()
            try:
                result = query_func(prompt)
                end_wall = time.time()
                duration = time.perf_counter() - start_perf
                log_llm_duration(lang, start_wall, end_wall, duration, success=True)
                outputs[lang] = result
                print(f"Generated code for {lang}: {str(result)[:100]}...")
            except Exception as inner_e:
                end_wall = time.time()
                duration = time.perf_counter() - start_perf
                log_llm_duration(lang, start_wall, end_wall, duration, success=False, error_message=str(inner_e))
                print(f"LLM query failed for {lang}: {inner_e}")
                outputs[lang] = None
            time.sleep(1)
        except Exception as e:
            print(f"LLM query failed for {lang}: {e}")
            outputs[lang] = None
    return outputs


def process_single_prompt(prompt_data: Dict[str, str], data_dir: str, model_name: str = None) -> None:
    prompt_id = prompt_data['id']
    prompt_text = prompt_data['text']

    print(f"\n{'='*60}")
    print(f"Processing Prompt ID: {prompt_id}")
    print(f"Using model: {model_name or 'Qwen/Qwen3-30B-A3B-Instruct-2507 (default)'}")
    print("Features: Translation + LLM generation (no parsing/visualization)")
    print(f"{'='*60}")

    prompt_dir = ensure_prompt_dir(data_dir, prompt_id)

    try:
        from Prompt_translation import normalize_text
        prompt_text = normalize_text(prompt_text)
    except Exception:
        pass

    # 1) Translate
    print("Translating prompt to multiple languages...")
    translations = translate_prompt(prompt_text)
    translated_path = os.path.join(prompt_dir, "translated_prompts.json")
    with open(translated_path, "w", encoding="utf-8") as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)
    print(f"Saved translations to {translated_path}")

    # 2) Query LLM
    llm_outputs = query_llm_for_translations(translations, model_name=model_name)
    llm_out_path = os.path.join(prompt_dir, "llm_output.json")
    with open(llm_out_path, "w", encoding="utf-8") as f:
        json.dump(llm_outputs, f, ensure_ascii=False, indent=2)
    print(f"Saved LLM outputs to {llm_out_path}")


def main() -> None:
    project_root = ensure_dirs()
    data_dir = os.path.join(project_root, "data")
    setup_logger()

    model_name: Optional[str] = None

    args = sys.argv[1:]
    if "--model" in args:
        model_idx = args.index("--model")
        if model_idx + 1 < len(args):
            model_name = args[model_idx + 1]

    json_file = None
    for arg in args:
        if not arg.startswith("--") and arg.endswith(".json"):
            json_file = arg
            break

    if json_file:
        try:
            prompts = load_prompts_from_json(json_file)
            print(f"Loaded {len(prompts)} prompts from {json_file}")

            for i, prompt_data in enumerate(prompts, 1):
                print(f"\nProcessing prompt {i}/{len(prompts)}")
                process_single_prompt(prompt_data, data_dir, model_name=model_name)

            print(f"\n{'='*60}")
            print("All prompts processed (translation + LLM).")
            print(f"Results saved per prompt under: {data_dir}")
            print(f"{'='*60}")

        except Exception as e:
            print(f"Error processing JSON file: {e}")
            return
    else:
        prompt_text = input("Enter the base prompt (in English): ").strip()
        if not prompt_text:
            print("Empty prompt; aborting.")
            return

        prompt_data = {
            'id': 'single_prompt',
            'text': prompt_text
        }

        process_single_prompt(prompt_data, data_dir, model_name=model_name)
        print("Two-step pipeline complete.")


if __name__ == "__main__":
    main()


