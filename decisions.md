## 2026-08-14 Postgres with pgvector, not SQLite

Chose Postgres running in Docker using the pgvector/pgvector:pg16 image.
SQLite would be simpler for local development but has no vector similarity search, which the retrieval phase depends on. Matching the locat database to what will run in production also avoids surprises at deployment.

## 2026-08-14 One Base, defined in database.py

All model classes import base from app/database.py rather than defining their own. Defining a second Base in models.py means the models register against a different metadata object, so create_all runs cleanly and creates nothing. The failure is silent: no error, no CREATE TABLE, just BEGIN and COMMIT. Cost about twenty minutes to find.

## 2026-08-14 Alembic over create_all

Replaced Base.metadata.create_all with Alembic migrations. create_all only creates tables that do not already exist, so any change to a model after the first run does nothing. Adding a column would mean dropping the table and losing the data. Alembic records each schema as a versioned, reversible file that lives in  git alongside the code