import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screener.cache import EvaluationCache, make_key  # noqa: E402
from screener.evaluator import ResumeEvaluator, build_prompt  # noqa: E402


class StubResponse:
    def __init__(self, text):
        self.text = text


class StubModel:
    def __init__(self):
        self.calls = 0

    def generate_content(self, prompt):
        self.calls += 1
        return StubResponse(f"Rating: 7/10\nFeedback: call {self.calls}")


class CacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = EvaluationCache(os.path.join(self.tmp.name, "test.db"))

    def tearDown(self):
        self.cache.close()
        self.tmp.cleanup()

    def test_key_ignores_whitespace_differences(self):
        self.assertEqual(make_key("a  b\n", "c"), make_key("a b", "c"))

    def test_key_separates_fields(self):
        self.assertNotEqual(make_key("ab", "c"), make_key("a", "bc"))

    def test_put_then_get(self):
        self.cache.put("k", "result")
        self.assertEqual(self.cache.get("k"), "result")
        self.assertIsNone(self.cache.get("missing"))

    def test_repeat_evaluation_skips_the_api(self):
        model = StubModel()
        evaluator = ResumeEvaluator(model, self.cache)
        first, cached1 = evaluator.evaluate("job", "resume")
        second, cached2 = evaluator.evaluate("job", "resume")
        self.assertEqual((cached1, cached2), (False, True))
        self.assertEqual(first, second)
        self.assertEqual(model.calls, 1)

    def test_different_resume_calls_the_api(self):
        model = StubModel()
        evaluator = ResumeEvaluator(model, self.cache)
        evaluator.evaluate("job", "resume one")
        evaluator.evaluate("job", "resume two")
        self.assertEqual(model.calls, 2)
        self.assertEqual(self.cache.count(), 2)

    def test_prompt_asks_for_formatting_and_grammar(self):
        prompt = build_prompt("JOB", "RESUME")
        for part in ("JOB", "RESUME", "Skill relevance", "Formatting", "Grammar"):
            self.assertIn(part, prompt)


if __name__ == "__main__":
    unittest.main()
