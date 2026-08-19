"""Run the eval set against the live system.

    python -m evals.run

Requires a Gemini API key and an ingested corpus. Not run in CI.
"""
import json
import time
from pathlib import Path

from google.genai import errors

from app.database import SessionLocal
from app.services.llm import structured_answer
from app.services.retrieval import format_context, retrieve

QUESTIONS = Path("evals/questions.jsonl")
PAUSE_SECONDS = 5
MAX_RETRIES = 4
RATE_LIMIT_WAIT = 60
RETRYABLE_SERVER_CODES = (500, 502, 503, 504)


def load_cases() -> list[dict]:
    return [
        json.loads(line)
        for line in QUESTIONS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def answer_with_retry(question: str, context: str):
    """Call the model, backing off on transient rate limits and server errors.

    A per-day quota is not transient, so it is raised immediately rather
    than slept through.
    """
    for attempt in range(MAX_RETRIES):
        try:
            return structured_answer(question, context)
        except errors.ClientError as exc:
            if exc.code != 429:
                raise
            if "PerDay" in str(exc):
                print("       daily quota exhausted, resume after 6pm Sydney")
                raise
            if attempt == MAX_RETRIES - 1:
                raise
            print(f"       rate limited, waiting {RATE_LIMIT_WAIT}s")
            time.sleep(RATE_LIMIT_WAIT)
        except errors.ServerError as exc:
            if exc.code not in RETRYABLE_SERVER_CODES or attempt == MAX_RETRIES - 1:
                raise
            wait = 10 * (attempt + 1)
            print(f"       server error {exc.code}, waiting {wait}s")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def check_text(answer_text: str, must_contain: list) -> bool:
    """Each entry is a string, or a list of acceptable phrasings."""
    lowered = answer_text.lower()
    for entry in must_contain:
        variants = entry if isinstance(entry, list) else [entry]
        if not any(v.lower() in lowered for v in variants):
            return False
    return True


def check_citations(clauses: list[str], must_cite: list[str]) -> bool:
    joined = " ".join(clauses).lower()
    return all(c.lower() in joined for c in must_cite)


def run() -> None:
    cases = load_cases()
    db = SessionLocal()
    passed_count = 0
    failures = []

    try:
        for i, case in enumerate(cases, start=1):
            question = case["question"]
            chunks = retrieve(db, question)
            answer = answer_with_retry(question, format_context(chunks))

            if case.get("expect_refusal"):
                passed = answer.confidence == "low" and not answer.clauses
                detail = "refused correctly" if passed else "answered when it should not have"
            else:
                text_ok = check_text(answer.answer, case.get("must_contain", []))
                cite_ok = check_citations(answer.clauses, case.get("must_cite", []))
                passed = text_ok and cite_ok
                detail = f"text={'ok' if text_ok else 'FAIL'} cite={'ok' if cite_ok else 'FAIL'}"

            print(f"[{i:>2}/{len(cases)}] {'PASS' if passed else 'FAIL'} | {detail} | {question[:55]}")

            if passed:
                passed_count += 1
            else:
                failures.append((question, detail))
                print(f"       answer:  {answer.answer[:200]}")
                print(f"       clauses: {answer.clauses}")
                print(f"       chunks:  {[c.source_ref for c in chunks]}")

            if i < len(cases):
                time.sleep(PAUSE_SECONDS)
    finally:
        db.close()

    total = len(cases)
    pct = 100 * passed_count / total if total else 0
    print(f"\n{'=' * 60}")
    print(f"{passed_count}/{total} passed ({pct:.0f}%)")
    print("Note: a single run is one sample. Scores vary by a question or two.")

    if failures:
        print(f"\n{len(failures)} failures:")
        for question, detail in failures:
            print(f"  - {detail} | {question[:60]}")


if __name__ == "__main__":
    run()