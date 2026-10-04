# ⚡ Jev Model — Question & Answer Suggestion Engine

A high-performance Question & Answer prediction and suggestion system powered by TypeSafe AI's **Jev Model** ("System One" non-autoregressive decision AI).

Unlike traditional large language models (LLMs) that generate conversational text token-by-token, **Jev** processes structured state and decision questions in a single pass at ultra-low latency (70–300ms) with mathematically calibrated probability distributions.

---

## 🚀 Features

- **Candidate Answer Suggestion (`Choice` primitive)**: Evaluates a question and set of candidate answers against context evidence, selecting the optimal answer and returning calibrated probability distributions for each option.
- **Quality & Impact Rubric (`Score` primitive)**: Rates answer reliability, relevance, and operational certainty along an ordered rubric scale.
- **Soundness & Truth Validation (`Noul` primitive)**: Computes a calibrated boolean probability (0.0 to 1.0) validating whether the suggested answer is sound and supported by context.
- **Interactive Web Dashboard**: Modern single-page app with visual probability bars, latency meters, preset loader, JSON payload inspector, and dynamic candidate option controls.
- **Interactive CLI**: Terminal tool for fast testing, preset evaluation, and interactive QA input.
- **Dual Execution Engine**:
  - **Live Mode**: Uses the official `typesafe-sdk` client when `TYPESAFE_API_KEY` is provided.
  - **Calibrated Simulation Mode**: Runs local System One non-autoregressive simulation for immediate testing without API key requirements.

---

## 📁 Project Structure

```
Jev Model/
├── app.py                      # Flask web server & REST API
├── jev_engine.py               # Core Jev engine (Choice, Score, Noul + simulation fallback)
├── cli.py                      # Command-line interface for Q&A prediction
├── requirements.txt            # Python dependencies (typesafe-sdk, flask, python-dotenv)
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
├── static/
│   ├── index.html              # Responsive web dashboard
│   ├── style.css               # Modern dark-mode styling
│   └── app.js                  # Frontend state management & visualization
├── presets/
│   └── sample_questions.json   # Pre-configured real-world scenarios
└── tests/
    └── test_jev_engine.py      # Automated unit & integration tests
```

---

## 🛠️ Getting Started

### 1. Installation

Ensure you have Python 3.10+ installed:
```bash
pip install -r requirements.txt
```

### 2. Configuration (Optional for Live Mode)

If you have a TypeSafe AI API key:
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Set your API key in `.env`:
   ```env
   TYPESAFE_API_KEY=your_typesafe_api_key_here
   ```
*(If no API key is provided, the engine will run in Calibrated Simulation Mode out of the box).*

---

## 🌐 Running the Web Dashboard

Start the Flask server:
```bash
python app.py
```
Open your browser at **[http://localhost:5000](http://localhost:5000)**.

### Using the Web UI:
1. Select a preset (e.g. *IT Incident Triage*, *Customer Support*, *Physics & Thermodynamics*, *Medical Triage*) or type your own question.
2. Add, remove, or modify candidate answers.
3. Click **"Predict Best Answer"** to execute.
4. View the suggested answer, calibrated probabilities, quality score, and raw JSON payload.

---

## 💻 Running the CLI

### 1. List Available Presets
```bash
python cli.py --list-presets
```

### 2. Run a Specific Preset
```bash
python cli.py --preset network_incident
python cli.py --preset customer_support
python cli.py --preset science_physics
python cli.py --preset medical_triage
```

### 3. Interactive Terminal Mode
```bash
python cli.py
```
Prompts you step-by-step for context, question, candidate options, and verification statement.

---

## 🧪 Running Automated Tests

Run the test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📡 REST API Reference

### `POST /api/suggest`
Predicts the best candidate answer and returns probability distributions.
```json
{
  "question": "What is the capital of France?",
  "context": "Paris is the capital of France.",
  "candidate_answers": [
    { "id": "A", "text": "Paris" },
    { "id": "B", "text": "London" },
    { "id": "C", "text": "Berlin" }
  ]
}
```

### `GET /api/presets`
Returns all pre-configured QA scenarios.

### `GET /api/status`
Returns SDK readiness and active execution mode.
