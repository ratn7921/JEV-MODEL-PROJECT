"""
Unit and integration tests for Jev QA Engine and Flask API
"""

import unittest
import json
from jev_engine import JevQAEngine
from app import app

class TestJevQAEngine(unittest.TestCase):

    def setUp(self):
        self.engine = JevQAEngine()
        self.sample_context = (
            "PostgreSQL primary db-01 connection pool exhausted due to runaway queries "
            "from worker-04. Immediate remediation is to terminate worker-04 queries and throttle pool."
        )
        self.sample_question = "What is the recommended immediate action?"
        self.sample_answers = [
            {"id": "A", "text": "Terminate worker-04 queries and throttle pool."},
            {"id": "B", "text": "Reboot the physical server and re-route traffic."},
            {"id": "C", "text": "Ignore the alert and wait 24 hours."}
        ]

    def test_engine_initialization(self):
        self.assertIsNotNone(self.engine)
        # Should be able to update key dynamically
        self.engine.set_api_key("test_key_123")
        self.assertEqual(self.engine.api_key, "test_key_123")
        self.engine.set_api_key("")

    def test_prediction_structure(self):
        result = self.engine.predict_and_suggest(
            question=self.sample_question,
            candidate_answers=self.sample_answers,
            context=self.sample_context,
            force_simulation=True
        )

        # Check required fields
        self.assertIn("selected_id", result)
        self.assertIn("suggested_text", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)
        self.assertIn("score", result)
        self.assertIn("noul", result)
        self.assertIn("latency_ms", result)

        # Choice A should win given the explicit context match
        self.assertEqual(result["selected_id"], "A")
        self.assertIn("Terminate worker-04", result["suggested_text"])

    def test_probabilities_normalization(self):
        result = self.engine.predict_and_suggest(
            question=self.sample_question,
            candidate_answers=self.sample_answers,
            context=self.sample_context,
            force_simulation=True
        )

        probs = result["probabilities"]
        self.assertEqual(len(probs), 3)
        total_p = sum(probs.values())
        self.assertAlmostEqual(total_p, 1.0, places=2)

    def test_validation_errors(self):
        # Empty question
        with self.assertRaises(ValueError):
            self.engine.predict_and_suggest(
                question="",
                candidate_answers=self.sample_answers
            )

        # Fewer than 2 answers
        with self.assertRaises(ValueError):
            self.engine.predict_and_suggest(
                question="Valid question?",
                candidate_answers=[{"id": "A", "text": "Only one option"}]
            )


class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_status_endpoint(self):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("status"), "ready")
        self.assertIn("typesafe_sdk_installed", data)
        self.assertIn("live_mode_active", data)

    def test_presets_endpoint(self):
        response = self.client.get("/api/presets")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("presets", data)
        self.assertGreater(len(data["presets"]), 0)

    def test_suggest_endpoint_success(self):
        payload = {
            "question": "Which gas is most abundant in Earth's atmosphere?",
            "context": "Earth's atmosphere is composed of approximately 78% Nitrogen and 21% Oxygen.",
            "candidate_answers": [
                {"id": "A", "text": "Nitrogen"},
                {"id": "B", "text": "Oxygen"},
                {"id": "C", "text": "Carbon Dioxide"}
            ],
            "force_simulation": True
        }
        response = self.client.post(
            "/api/suggest",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get("selected_id"), "A")
        self.assertEqual(data.get("suggested_text"), "Nitrogen")
        self.assertGreater(data.get("confidence", 0), 0.5)

    def test_suggest_endpoint_missing_question(self):
        payload = {
            "question": "",
            "candidate_answers": [{"id": "A", "text": "One"}, {"id": "B", "text": "Two"}]
        }
        response = self.client.post(
            "/api/suggest",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_evaluate_endpoint(self):
        payload = {
            "question": "What is 2 + 2?",
            "answer_text": "4",
            "context": "Basic arithmetic defines 2 + 2 = 4."
        }
        response = self.client.post(
            "/api/evaluate",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("score", data)
        self.assertIn("noul", data)

if __name__ == "__main__":
    unittest.main()
