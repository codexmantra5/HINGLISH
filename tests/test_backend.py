import json
import unittest
from unittest.mock import MagicMock, patch

import backend.server as server


class AnalyzeComplaintTests(unittest.TestCase):
    def test_gemini_free_tier_reports_zero_cost(self):
        response_body = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "department": "Plumbing",
                        "confidence": 0.94,
                    })
                }
            }],
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 30,
            },
        }
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(response_body).encode("utf-8")

        with patch.dict(server.os.environ, {}, clear=True), patch.multiple(
            server,
            AI_API_KEY="test-key",
            AI_MODEL="gemini-3.5-flash-lite",
            AI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai",
        ), patch("backend.server.urllib.request.urlopen", return_value=response):
            result = server.analyze_complaint("Bhai washroom ka tap leak kar raha hai")

        self.assertEqual(result["cost"], 0.0)
        self.assertEqual(result["model"], "gemini-3.5-flash-lite")


if __name__ == "__main__":
    unittest.main()
