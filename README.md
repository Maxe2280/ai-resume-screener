# AI Resume Screener

A desktop app that scores a resume against a job description with the Gemini API. Paste a job
description, pick a PDF or DOCX resume, and it returns a rating out of 10 with feedback on skill
relevance, formatting, and grammar.

## How it works

The code is split into three parts:

| Module | Job |
|---|---|
| `screener/extract.py` | Input handling: reads text out of PDF (PyMuPDF) and DOCX (python-docx) files |
| `screener/evaluator.py` | AI logic: builds the prompt and calls Gemini (`gemini-2.0-flash`) |
| `screener/cache.py` | Data persistence: a SQLite cache of past evaluations |
| `app.py` | The Tkinter interface |

**Caching.** Each evaluation is stored in `evaluations.db`, keyed by a SHA-256 hash of the model
name, the prompt version, the job description, and the resume text (whitespace-normalized). If you
evaluate the same resume against the same job again, the result comes from the cache instead of a
new API call, so it is instant and costs nothing. Changing the prompt bumps `PROMPT_VERSION`, so old
answers are never reused for a different prompt.

**Prompting.** The prompt asks for a fixed output format (rating, then skill relevance, formatting,
grammar, and a feedback paragraph), which keeps the feedback consistent from run to run. Grammar
issues are quoted with a suggested fix so they are actionable.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env   # then put your Gemini API key in .env
python app.py
```

Get a Gemini API key at https://aistudio.google.com/apikey. The `.env` file and the cache database
are gitignored.

`samples/` has a job description and a fictional resume to try it with.

## Tests

```bash
python -m unittest discover tests
```

The tests cover the cache and the evaluator's cache logic with a stub model, so they need no API key.
