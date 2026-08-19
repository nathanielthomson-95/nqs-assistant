# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Add GET /documents and POST /documents using Depends(get_db)
- Read the FastAPI docs page on dependencies

# Next session

- docker compose up -d, activate .venv, alembic upgrade head
- install pytest and httpx
- Write tests for the document routes
- Read the FastAPI testing docs

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- set up GitHub Actions to run pytest on every push
- Add a build badge to the README

# Next session

- docker compose -d, activate .venv, alembic upgrade head
- Restructure: move business logic out of routers into app/services/
- Ass a POST /centres route and test to match

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Phase 2 begins: first direct model call, replacing the hardcoded /ask
- Log token counts and cost from the very first call

## Before starting

- Anthropic API key from console.anthropic.com, ~$10 credit
- Key goes in .env, confirm .env is in .gitignore first

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Move SYSTEM_PROMPT out of llm.py into a versioned prompts/ file
- Structured output: ask for JSON, validate with Pydantic

# Next session

- docker compose up -d, activate .venv, alembic upgrade head
- Download the NQS and National Regulations source documents
- Write the chunking function, store chunks with source references

# Next session

- docker compose up -d, activate .venv, alembic upgrade head
- Enable the pgvector extension, add the embedding column
- Generate embeddings with gemini-embedding-001, store them

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Enable the pgvector extension, add the embedding column
- Generate embeddings with gemini-embedding-001, store them

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Retrieval query using the <=> cosine operator
- Join retrieval to structured_answer, pass real context
- First real citations

# Next session

- docker compose up -d
- Activate .venv, then alembic upgrade head
- Write 30 eval questions with known answers into evals/questions.jsonl
- Build the eval runner, get a first pass rate
- Tune the 0.55 similarity floor against the results

# Next session

- Daily Gemini quota resets 6pm Sydney. Do not start ingest before then.
- docker compose up -d, activate .venv, alembic upgrade head
- TRUNCATE chunks, re-ingest (342 chunks, ~15 min with throttling)
- python -m evals.run, record the number against 86%

# Phase 3 plan

14. API shape: headline field, citations carry their text, ratio endpoint
15-17. Frontend: Vite + React + TS + Tailwind, mobile first
18. Streaming via SSE
19-20. Jurisdiction: tag chunks, filter retrieval, setup screen

Rationale: API shape first so the frontend is only built once. Jurisdiction
last because it needs a re-ingest, new eval cases and a UI flow.

# Next session (14)

- docker compose up -d, activate .venv, alembic upgrade head
- Add headline: str to ComplianceAnswer, update prompts/answer_json.md
- Change clauses to list[Citation] with reference, content, similarity
- Add POST /ratio, pure calculation, no model call
- Tests for all three
- Re-run evals: check_citations will need updating for the new shape

## Product decisions to make in Phase 3

Design for a centre director on their phone, standing in a room, not at a
desk. In rough priority:

1. Jurisdiction picked once at setup, then filtered silently
2. Lead with the answer, not the paragraph (add a headline field)
3. Citations that expand to show the retrieved regulation text
4. A ratio calculator alongside the Q&A, no model call needed
5. Streaming, so three seconds does not feel broken

## Known, deferred

- Eval set saturated at 28-29/29. Needs harder questions before it can
  measure anything: multi-regulation answers, jurisdictional overrides,
  false-premise questions.
- Regulation 1 is titled "Title", too short for the heading pattern, so it
  falls into a page-level chunk. Deliberate trade-off.
- Bump actions/checkout to v5, setup-python to v6.

## Rules worth keeping

- pip freeze > requirements.txt immediately after any pip install
- pytest locally before every push
- Low priority: bump actions/checkout to v5, setup-python to v6

## Git workflow reminder

git switch -c feat/some-name
git status
git add .
git commit -m "..."
git push -u origin feat/some-name
PR on GitHub - Read diff - Merge - Delete branch
git switch main
git pull