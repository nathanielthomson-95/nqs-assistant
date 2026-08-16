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