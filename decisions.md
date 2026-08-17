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

## 2026-08-14 Routers handle HTTP, services own the data

Split the database work out of the route functions into app/services/.
Routers now validate the request, call a service function, and return.
Services take a session and do the SQLAlchemy work.

Two reasons. Route functions stay short enough to read at a glance, which
matters when someone opens the repo cold. And the logic can be tested
without going through HTTP if that ever becomes useful.

Evidence the split was clean: all seven existing document tests passed
unchanged after every line of database code moved into a new layer. No
test knew the difference, which is the point.

## 2026-08-16 Gemini free tier over a paid API

Using Google Gemini via AI Studio rather than a paid provider. No credit
card, and the free tier covers development volume comfortably. All
provider-specific code lives in app/services/llm.py, so swapping later is
a one-file change.

Trade-off: free tiers can tighten rate limits without warning and go down
with no compensation. Fine for development and a portfolio demo, not for
anything anyone depends on.

## 2026-08-16 Model identifiers are volatile

gemini-2.5-flash returned a 404 saying it is no longer available to new
users. models.list() shows what exists, not what a given key can call, so
the only real test is making the call. Also avoiding the -latest aliases,
since they move underneath you and would make eval results
irreproducible.

The error was one line at the bottom of a sixty-line framework traceback.
Reading tracebacks from the bottom up is the habit that found it.

## 2026-08-16 Push protection caught a hardcoded key

GitHub push protection blocked a push containing the Gemini key in two
places: as the default value of gemini_api_key in config.py, and copied
into .env.example. Nothing reached GitHub.

Fixed by regenerating the key, emptying both, and rewriting the branch
history with git reset --soft rather than clicking the unblock link.

Two rules from this. A settings default is a public value by definition,
so it can never hold a secret. And .env.example documents variable names,
never values.## 2026-08-16 Gemini free tier over a paid API

Using Google Gemini via AI Studio rather than a paid provider. No credit
card, and the free tier covers development volume comfortably. All
provider-specific code lives in app/services/llm.py, so swapping later is
a one-file change.

Trade-off: free tiers can tighten rate limits without warning and go down
with no compensation. Fine for development and a portfolio demo, not for
anything anyone depends on.

## 2026-08-16 Model identifiers are volatile

gemini-2.5-flash returned a 404 saying it is no longer available to new
users. models.list() shows what exists, not what a given key can call, so
the only real test is making the call. Also avoiding the -latest aliases,
since they move underneath you and would make eval results
irreproducible.

The error was one line at the bottom of a sixty-line framework traceback.
Reading tracebacks from the bottom up is the habit that found it.

## 2026-08-16 Push protection caught a hardcoded key

GitHub push protection blocked a push containing the Gemini key in two
places: as the default value of gemini_api_key in config.py, and copied
into .env.example. Nothing reached GitHub.

Fixed by regenerating the key, emptying both, and rewriting the branch
history with git reset --soft rather than clicking the unblock link.

Two rules from this. A settings default is a public value by definition,
so it can never hold a secret. And .env.example documents variable names,
never values.

## 2026-08-16 Prompts as versioned files, structured output validated

Prompts moved out of Python strings into prompts/*.md. They will change
constantly, and a markdown diff is readable in a way a diff of a
triple-quoted string is not.

/ask now returns validated JSON rather than free text, via a
ComplianceAnswer Pydantic model with a Literal on the confidence field.
json.loads only proves the response is valid JSON, not that it has the
shape asked for, so validation happens at the boundary and fails loudly.
One retry on malformed output, since roughly one response in fifty comes
back wrong and a second attempt almost always fixes it.

Markdown fences are stripped defensively. The model wraps JSON in them
regardless of instructions.

## 2026-08-16 Source documents stay out of the repo

The NQS and National Regulations PDFs live in data/raw/, which is
gitignored. Two reasons: git stores every version of every file forever,
so a 20MB PDF committed three times is 60MB in the repo permanently, and
the documents are ACECQA's to distribute, not mine.

A committed .gitkeep preserves the folder structure so a fresh clone has
somewhere to put them, with the ingest path documented in the README.

## 2026-08-16 Structural chunking, and source refs from the start

Chunking on regulation boundaries rather than fixed-size windows. A clause
cut in half retrieves badly and cites worse, and regulatory text has clean
structure to split on, so fixed windows throw away information the
document is handing over for free.

Every chunk carries a source_ref (regulation number and page) from the
moment it is created. Citations cannot be retrofitted without reprocessing
the whole corpus, and citation accuracy is the point of the project rather
than a nice-to-have.

Started with a naive fixed-size splitter first to understand the failure
mode before replacing it.

## 2026-08-16 Source documents stay out of the repo

The NQS and National Regulations PDFs live in data/raw/, gitignored. Git
stores every version of every file forever, so a 20MB PDF committed three
times is 60MB in the repo permanently. They are also ACECQA's documents,
not mine to redistribute. A committed .gitkeep preserves the folder so a
fresh clone has somewhere to put them.

## 2026-08-16 Structural chunking, and source refs from the start

Chunking on regulation boundaries rather than fixed-size windows. A clause
cut in half retrieves badly and cites worse, and regulatory text has clean
structure to split on, so fixed windows throw away information the
document hands over for free. Wrote the naive fixed-size version first to
understand the failure mode before replacing it.

Every chunk carries a source_ref (regulation number and page) from the
moment it is created. Citations cannot be retrofitted without reprocessing
the whole corpus, and citation accuracy is the point of this project.

## 2026-08-16 A hang is a worse failure than a wrong answer

A typo in the chunking loop stopped start advancing, so the loop never
terminated. CI gave no traceback, just exit code 143 after a timeout, and
it took two runs to work out it was a hang rather than a cancelled job.

Two fixes. A guard clause rejecting overlap >= size turns a silent hang
into an immediate readable error. And pytest-timeout, added locally and to
the workflow, so a hang fails in ten seconds instead of burning a CI run.

Broader lesson: run pytest locally before pushing. CI is for catching what
my machine hides, not for finding typos.

## 2026-08-16 pgvector in the existing Postgres

Vectors live in the same Postgres the rest of the app uses, via the
pgvector extension, rather than in a dedicated vector database. It
handles this scale comfortably, and "I used the database I already had"
is a better engineering answer than "I added a service".

## 2026-08-16 768 dimensions, not 3072

gemini-embedding-001 returns 3072 dimensions by default. Requested 768
via output_dimensionality instead, because pgvector's HNSW index caps at
2000 dimensions, and an unindexed vector column means sequential scans
forever. Storage drops to a quarter with no meaningful retrieval quality
loss on a single regulatory corpus.

Also typed 3702 instead of 3072 when first creating the column. Caught it
before ingesting. Two minutes to fix at that point, versus a full re-embed
of the corpus if it had been found later. The dimension is fixed when the
column is created.

## 2026-08-16 Free tier counts texts, not calls

Hit a 429 after 100 chunks. The quota is 100 embed requests per minute,
and a batch of 50 texts counts as 50 requests, so batching reduces round
trips but not quota usage.

Handled with 25-chunk batches, a 20 second pause between them, and
exponential backoff on 429. 442 chunks now ingests in about six minutes.
This is the trade-off accepted by choosing the free tier, and a paid key
would be the first change if this ever served real users.

## 2026-08-16 Test fixtures provision what they need

The test database had no pgvector extension, so every test errored with
"type vector does not exist". Fixed by having the db_session fixture run
CREATE EXTENSION IF NOT EXISTS vector itself rather than assuming a
prepared database.

Doing it by hand would have fixed my machine and left CI broken. Same
principle as requirements.txt: a fresh machine should run the suite with
nothing but the repo.

## 2026-08-16 Retrieval joined to the answer

/ask now embeds the question, pulls the nearest chunks from pgvector, and
passes them to the model as context. Citations come from the source_ref
attached to each chunk at ingest time rather than from the model's
training data.

Retrieving five chunks rather than one, because ratios vary by age band
and by jurisdiction, so a correct answer often needs several regulations
in context at once. Testing the retrieval query directly showed the right
regulation at 0.86 similarity with four genuinely relevant neighbours
between 0.79 and 0.82.

Each chunk is labelled with its source reference inside the context
block. The model can only cite what it can see.

## 2026-08-16 A similarity floor rather than always answering

Chunks below 0.55 similarity are dropped. If nothing clears the floor the
model gets no context at all and is instructed to say so, with an empty
clauses list and low confidence.

Without a floor the system would always find a nearest chunk, however
irrelevant, and answer confidently from it. In a compliance context a
confident wrong answer is worse than no answer, so the failure mode has
to be an honest refusal.

The threshold is a first guess and will be tuned against the eval set.

## 2026-08-16 Retrieved text is data, not instruction

The system prompt states that everything in the context is reference
material and never an instruction to follow. Basic prompt injection
defence, cheap to add now, and necessary once documents can be uploaded
rather than only ingested by me.