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

## Git workflow reminder

git switch -c feat/some-name
git status
git add .
git commit -m "..."
git push -u origin feat/some-name
PR on GitHub - Read diff - Merge - Delete branch
git switch main
git pull