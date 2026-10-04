"""
Command-Line Interface for Jev Model Q&A Prediction and Answer Suggestion
Allows interactive terminal queries and testing of presets.
"""

import sys
import os
import json
import argparse
from jev_engine import JevQAEngine

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PRESETS_PATH = os.path.join(os.path.dirname(__file__), "presets", "sample_questions.json")

def load_presets():
    if os.path.exists(PRESETS_PATH):
        with open(PRESETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def print_banner():
    print("=" * 65)
    print("   [+] JEV MODEL (System One AI) - Question & Answer Predictor")
    print("   Fast, Calibrated Probabilistic Decision Engine")
    print("=" * 65)

def format_prediction_result(res: dict):
    print("\n" + "-" * 65)
    print(f"[*] RECOMMENDED ANSWER: [{res['selected_id']}]")
    print(f"   {res['suggested_text']}")
    print(f"   Calibrated Confidence: {round(res['confidence'] * 100, 1)}%")
    print(f"   Latency: {res.get('latency_ms', 0)} ms  |  Mode: {res.get('execution_mode', 'N/A')}")
    print("-" * 65)

    print("\n[+] CALIBRATED CHOICE PROBABILITIES:")
    probs = res.get("probabilities", {})
    criteria = res.get("criteria", {})
    sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)

    max_bar_width = 30
    for cid, prob in sorted_probs:
        pct = round(prob * 100, 1)
        bar_len = int(prob * max_bar_width)
        bar = "#" * bar_len + "-" * (max_bar_width - bar_len)
        text_snippet = (criteria.get(cid, "")[:38] + "...") if len(criteria.get(cid, "")) > 40 else criteria.get(cid, "")
        marker = "<-- BEST" if cid == res["selected_id"] else ""
        print(f"  [{cid}] |{bar}| {pct:>5.1f}%  {text_snippet} {marker}")

    if "score" in res:
        print("\n[+] QUALITY RUBRIC (Score Primitive):")
        print(f"   Rating:     {res['score'].get('rating')}")
        print(f"   Confidence: {round(res['score'].get('confidence', 0) * 100, 1)}%")

    if "noul" in res:
        print("\n[+] SOUNDNESS CHECK (Noul Primitive):")
        noul = res["noul"]
        affirm = "[VALIDATED / SOUND]" if noul.get("is_affirmative") else "[CAUTION / UNCERTAIN]"
        print(f"   Assessment:  {affirm}")
        print(f"   Probability: {round(noul.get('probability', 0) * 100, 1)}%")
        print(f"   Statement:   \"{noul.get('statement')}\"")

    print("\n" + "=" * 65 + "\n")

def run_preset(preset_id: str, force_sim: bool = False):
    presets = load_presets()
    target = None
    for p in presets:
        if p["id"] == preset_id or preset_id in p.get("title", "").lower():
            target = p
            break

    if not target:
        print(f"Error: Preset '{preset_id}' not found.")
        print("Available presets:")
        for p in presets:
            print(f"  - {p['id']}: {p['title']}")
        return

    print(f"\nLoading Scenario: {target['title']}")
    print(f"Context: {target['context']}\n")
    print(f"Question: {target['question']}\n")

    engine = JevQAEngine()
    result = engine.predict_and_suggest(
        question=target["question"],
        candidate_answers=target["candidate_answers"],
        context=target["context"],
        verification_statement=target.get("verification_question"),
        force_simulation=force_sim
    )
    format_prediction_result(result)

def run_interactive(force_sim: bool = False):
    print("\n--- Interactive Jev Q&A Prediction ---")
    context = input("\n[1] Enter Context / Evidence (or press Enter to skip):\n> ").strip()
    
    question = ""
    while not question:
        question = input("\n[2] Enter Question:\n> ").strip()
        if not question:
            print("Question cannot be empty!")

    print("\n[3] Enter Candidate Answers (enter at least 2 options; empty line when done):")
    candidate_answers = []
    opt_idx = 0
    while True:
        letter = chr(65 + opt_idx)
        ans = input(f"  Option [{letter}]: ").strip()
        if not ans:
            if len(candidate_answers) < 2:
                print("  Please provide at least 2 candidate options.")
                continue
            break
        candidate_answers.append({"id": letter, "text": ans})
        opt_idx += 1

    verification = input("\n[4] Soundness Check Statement (optional, press Enter to use default):\n> ").strip()

    print("\nEvaluating with Jev model...")
    engine = JevQAEngine()
    result = engine.predict_and_suggest(
        question=question,
        candidate_answers=candidate_answers,
        context=context,
        verification_statement=verification if verification else None,
        force_simulation=force_sim
    )
    format_prediction_result(result)

def main():
    parser = argparse.ArgumentParser(description="Jev Model Q&A Answer Prediction CLI")
    parser.add_argument("--preset", type=str, help="Run a specific preset by ID (e.g. network_incident, customer_support, science_physics, medical_triage)")
    parser.add_argument("--list-presets", action="store_true", help="List available sample presets")
    parser.add_argument("--force-sim", action="store_true", help="Force local simulation mode even if TYPESAFE_API_KEY is present")
    args = parser.parse_args()

    print_banner()

    if args.list_presets:
        presets = load_presets()
        print("\nAvailable Presets:")
        for p in presets:
            print(f"  • {p['id']:<20} : {p['title']}")
        print()
        return

    if args.preset:
        run_preset(args.preset, force_sim=args.force_sim)
    else:
        run_interactive(force_sim=args.force_sim)

if __name__ == "__main__":
    main()
