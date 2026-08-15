## 2026-08-14 Postgres with pgvector, not SQLite

Chose Postgres running in Docker using the pgvector/pgvector:pg16 image.
SQLite would be simpler for local development but has no vector similarity search, which the retrieval phase depends on. Matching the locat database to what will run in production also avoids surprises at deployment.

## 2026-08-14 One Base, defined in database.py

All model classes import base from app/database.py rather than defining their own. Defining a second Base in models.py means the models register against a different metadata object, so create_all runs cleanly and creates nothing. The failure is silent: no error, no CREATE TABLE, just BEGIN and COMMIT. Cost about twenty minutes to find.

## 2026-08-14 Alembic over create_all

Replaced Base.metadata.create_all with Alembic migrations. create_all only creates tables that do not already exist, so any change to a model after the first run does nothing. Adding a column would mean dropping the table and losing the data. Alembic records each schema as a versioned, reversible file that lives in  git alongside the code

## 2026-08-14 Separate test database

Tests run against a second database, nqs_test, inside the same Postgres
container. Tables are created and dropped around every test by the
db_session fixture, so no test can depend on another one's leftovers, and
nothing can touch development data. The FastAPI dependency_overrides
mechanism swaps the real get_db for a test session, which only works
because the routes take the session via Depends rather than opening it
themselves.

## 2026-08-14 Import order broke the test fixtures

conftest.py had `from app.main import app` followed by `import app.models`.
The second line rebinds the name `app` from the FastAPI instance back to
the package, so every test errored with
"module 'app' has no attribute 'dependency_overrides'". The error pointed
at the fixture, but the cause was an import three lines earlier silently
overwriting a name. Fixed with `import app.models as _models`, which binds
a different name. Cost about fifteen minutes.