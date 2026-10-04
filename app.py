"""
Flask Application for Jev Model Q&A Prediction and Answer Suggestion
Exposes REST API endpoints and serves the modern interactive dashboard.
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from jev_engine import JevQAEngine, HAS_TYPESAFE_SDK

app = Flask(__name__, static_folder="static")

# Shared engine instance
engine = JevQAEngine()

PRESETS_PATH = os.path.join(os.path.dirname(__file__), "presets", "sample_questions.json")

def load_presets():
    if os.path.exists(PRESETS_PATH):
        try:
            with open(PRESETS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading presets: {e}")
    return []

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/status", methods=["GET"])
def get_status():
    """Return system readiness, SDK detection, and live/simulation mode status."""
    return jsonify({
        "status": "ready",
        "typesafe_sdk_installed": HAS_TYPESAFE_SDK,
        "live_mode_active": engine.is_live_mode_available(),
        "has_env_key": bool(os.environ.get("TYPESAFE_API_KEY", "").strip()),
        "default_model": "jev-latest" if engine.is_live_mode_available() else "jev-simulator-v1"
    })

@app.route("/api/presets", methods=["GET"])
def get_presets():
    """Return pre-configured real-world QA scenarios."""
    presets = load_presets()
    return jsonify({"presets": presets})

@app.route("/api/suggest", methods=["POST"])
def suggest_answer():
    """
    Main prediction endpoint.
    Accepts:
      - question: string (required)
      - candidate_answers: list of {id, text} (at least 2 required)
      - context: string (optional)
      - verification_statement: string (optional)
      - api_key: string (optional, overrides default key)
      - force_simulation: bool (optional)
    """
    data = request.get_json(force=True) or {}
    question = data.get("question", "").strip()
    candidate_answers = data.get("candidate_answers", [])
    context = data.get("context", "")
    verification_statement = data.get("verification_statement", "")
    custom_api_key = data.get("api_key", "").strip()
    force_sim = bool(data.get("force_simulation", False))

    if not question:
        return jsonify({"error": "Question is required."}), 400

    if not candidate_answers or len(candidate_answers) < 2:
        return jsonify({"error": "Please provide at least 2 candidate answers."}), 400

    # If user provided a specific API key for this request, instantiate engine with it
    active_engine = JevQAEngine(api_key=custom_api_key) if custom_api_key else engine

    try:
        prediction = active_engine.predict_and_suggest(
            question=question,
            candidate_answers=candidate_answers,
            context=context,
            verification_statement=verification_statement,
            force_simulation=force_sim
        )
        return jsonify(prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/evaluate", methods=["POST"])
def evaluate_specific_answer():
    """
    Evaluates a specific answer's quality and factual soundness.
    """
    data = request.get_json(force=True) or {}
    question = data.get("question", "").strip()
    answer_text = data.get("answer_text", "").strip()
    context = data.get("context", "")
    custom_api_key = data.get("api_key", "").strip()

    if not question or not answer_text:
        return jsonify({"error": "Both question and answer_text are required."}), 400

    active_engine = JevQAEngine(api_key=custom_api_key) if custom_api_key else engine

    try:
        # Formulate dummy alternative to run choice/scoring
        candidate_answers = [
            {"id": "TARGET", "text": answer_text},
            {"id": "GENERIC", "text": "Alternative unverified proposal."}
        ]
        prediction = active_engine.predict_and_suggest(
            question=question,
            candidate_answers=candidate_answers,
            context=context,
            verification_statement=f"Is the answer '{answer_text[:50]}' accurate and reliable?"
        )
        return jsonify({
            "answer_text": answer_text,
            "score": prediction.get("score"),
            "noul": prediction.get("noul"),
            "latency_ms": prediction.get("latency_ms"),
            "execution_mode": prediction.get("execution_mode")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Jev Model Q&A Server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
