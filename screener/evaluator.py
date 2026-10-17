"""AI logic: build the prompt, call Gemini, and reuse cached results."""
from .cache import make_key

MODEL_NAME = "gemini-2.0-flash"
# Bump when the prompt changes so old cached answers are not reused for the new prompt
PROMPT_VERSION = "2"

PROMPT_TEMPLATE = """
You are an AI resume screener. Evaluate the following resume for this job description.

Job Description:
{job_description}

Resume:
{resume_text}

Evaluate three things:
1. Skill relevance: how well the resume's skills and experience match the job.
2. Formatting: structure, section order, consistency, and readability.
3. Grammar: spelling, grammar, and wording problems, quoting the exact phrase.

Output format:
Rating: <number>/10
Skill relevance: <strong matches and missing skills>
Formatting: <specific, actionable suggestions>
Grammar: <each issue as "phrase" -> suggested fix, or "No issues found">
Feedback: <a short paragraph explaining the rating>
"""


def build_prompt(job_description, resume_text):
    return PROMPT_TEMPLATE.format(job_description=job_description, resume_text=resume_text)


class ResumeEvaluator:
    def __init__(self, model, cache):
        self.model = model
        self.cache = cache

    def evaluate(self, job_description, resume_text):
        """Return (result_text, from_cache)."""
        key = make_key(MODEL_NAME, PROMPT_VERSION, job_description, resume_text)
        cached = self.cache.get(key)
        if cached is not None:
            return cached, True
        response = self.model.generate_content(build_prompt(job_description, resume_text))
        result = response.text.strip()
        self.cache.put(key, result)
        return result, False
