"""Input handling: turn a resume file into plain text."""
import os

import docx
import fitz  # PyMuPDF

SUPPORTED = (".pdf", ".docx")


def extract_text_from_pdf(file_path):
    with fitz.open(file_path) as doc:
        return "".join(page.get_text() for page in doc)


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_resume_text(file_path):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    raise ValueError("Only PDF or DOCX files are supported.")
