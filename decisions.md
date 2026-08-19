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

## 2026-08-17 First eval baseline: 22/30 (73%)

Thirty questions covering ratios, space requirements, record keeping,
qualifications, notification timeframes and policies, plus five questions
the corpus cannot answer. Expected values verified against the source PDF,
not against the system's own answers. An eval set built from the system's
output would score near 100% and measure nothing.

22/30 passed. Recorded before any tuning.

The first attempt at this run scored 20%, but that measured the eval file
rather than the system: most expected values were still TODO placeholders,
so correct answers were being compared against the literal string "TODO".
Worth remembering that a first eval run often grades the grader.

## 2026-08-17 Chapter 7 crowds out the base regulations

The most serious failure was not a refusal or a bad citation. Asked for
the educator to child ratio for children aged 24 to 36 months, the system
answered 1 educator to 4 children. The correct figure is 1 to 5, in
Regulation 123.

The retrieved chunks explain it: 357, 275, 326, 342, 263. Regulation 123
never reached the model. Everything above roughly 260 is Chapter 7,
jurisdiction-specific and transitional provisions that are semantically
near-identical to the base regulations, so on ratio questions they take
every retrieval slot.

This is exactly the failure mode the project exists to avoid: a confident,
plainly stated, wrong compliance answer. Retrieval quality, not model
quality.

Two other real defects found in the same run, both deferred so that only
one variable changes at a time:

- Regulation 183 runs across pages 191 and 192. The continuation page has
  no heading, so it was chunked with a bare "page 192" reference. The
  answer was right and the citation was unusable. Fix is to carry the last
  seen regulation number forward across page boundaries at ingest.
- The refusal check requires an empty clauses list, but the model can
  decline in substance while still attaching page references. Either
  loosen the check or instruct the prompt to return no clauses when
  declining.

Also removed one eval question as invalid rather than fixing the system
around it. "What are the seven quality areas of the NQS" was written as a
refusal case, but the retrieved chunks came from pages 327 to 335: the NQS
is a schedule to the National Regulations, so the corpus does contain it.
Expecting a refusal for something the documents hold was my error, not the
system's. 29 questions from here, so the next score is not directly
comparable to 73%.

## 2026-08-17 TOP_K 5 to 8: 73% to 83%

Chapter 7 jurisdictional provisions were filling all five retrieval slots
on ratio questions. Eight slots let the base regulations through. Also
fixed two citation failures as a side effect.

## 2026-08-17 Regulations split across pages lost their identity

Four of the five remaining failures had one cause. Regulation 123 breaks
across pages 134 and 135: the birth-to-24-months ratio is on the labelled
chunk, and the 1:5 ratio, the 1:11 ratio and the mixed-ages subregulation
are all on the following page in a chunk with no heading. Regulation 120
splits the same way.

Two defects in the chunker. Continuation text got a bare page reference
instead of inheriting the regulation it belongs to. And text before the
first heading on a page was discarded entirely, which is precisely where
continuations live.

Fixed by carrying the last seen regulation number across page boundaries
and capturing the leading text. Before: X/29. After: Y/29.

The lesson is that chunk boundaries are not a formatting detail. A
document's page breaks have nothing to do with its logical structure, and
chunking that follows pages will cut clauses in half and strand the half
that answers the question.

## 2026-08-18 Regulations split across pages lost their identity

Four of five remaining eval failures had one cause. Regulation 123 breaks
across pages 134 and 135: the birth-to-24-months ratio sits in the
labelled chunk, while the 1:5 ratio, the 1:11 ratio and the mixed-ages
subregulation are all on the following page in a chunk with no heading.
Regulation 120 splits the same way.

Two defects in the chunker. Continuation text got a bare page reference
instead of inheriting the regulation it belongs to. And text before the
first heading on a page was discarded entirely, which is exactly where
continuations live.

Fixed by carrying the last seen regulation number across page boundaries,
capturing the leading text, and then merging chunks that share a
regulation number into one. 566 chunks extracted, 342 after merging.

Chunk boundaries are not a formatting detail. A document's page breaks
have nothing to do with its logical structure, and chunking that follows
pages will cut clauses in half and strand the half that answers the
question.

## 2026-08-18 Regulation numbers ascend, so they can validate themselves

The chunker was matching numbered list items as headings. "Regulation 2"
appeared eight times across pages 27 to 167, because a line like
"2 Fire and other emergencies" inside another regulation is
indistinguishable from a heading by appearance.

It is distinguishable by position. Regulation numbers ascend through the
document, so a heading numbered below the highest already seen cannot be
real. Tracking the highest number seen and rejecting anything lower
removed the false matches without touching the regex.

Known trade-off: the pattern requires at least ten characters of title,
which rejects list items like "2 Fire." but also rejects Regulation 1,
titled simply "Title". It falls into a page-level chunk instead. Accepted,
since loosening the rule brings the false matches back and nothing in the
eval set depends on Regulation 1.

## 2026-08-18 Embedding cache keyed by content hash

Re-ingesting after a chunking change re-embedded the entire corpus every
time, and four runs in one day exhausted the 1000-request daily free tier
quota. The chunk text barely changes between runs, so paying to embed it
repeatedly was pure waste.

Embeddings are now cached in data/embedding_cache.json keyed by a SHA-256
hash of the chunk text, and the cache is saved after every batch so a
failed run keeps its progress. Only genuinely new or changed chunks cost
quota.

## 2026-08-18 A 429 does not always mean wait

Two different quotas return the same status code and need opposite
responses. A per-minute limit is transient and exponential backoff is
correct. A per-day limit does not recover in seconds, and backing off
against it just sleeps five minutes before failing anyway, which is what
happened.

The retry logic now inspects the error body for "PerDay" and raises
immediately with a message rather than retrying. Reading the quota name
in the error rather than just the status code is the difference.

Also worth recording: the daily quota resets at midnight Pacific, which is
6pm Sydney. Limits are per Google Cloud project, not per API key.

## 2026-08-18 A function that is never called fails silently

merge_by_regulation was written correctly and never wired into the ingest
loop. Nothing errored. The only visible symptom was a chunk count that
went up when it should have gone down, and that was only visible because
the script prints counts at each stage.

Added a second print after merging so the two numbers can be compared at a
glance. Cheap instrumentation between pipeline stages pays for itself.

## 2026-08-19 Merging split regulations: 86% to 97%

Regulation 123 is now a single chunk containing all three ratios rather
than two chunks split at a page break. Q3, Q14, Q24 and Q25 all passed
after the change.

Full progression: 73% baseline, 83% (TOP_K 5 to 8), 86% (carry regulation
number across page breaks), 97% (merge split regulations). Every gain came
from retrieval quality. The model and the prompt were never the problem.

One remaining failure: the policies question. Regulation 168 lists roughly
fifteen matters and the model summarises rather than enumerating. Left
failing rather than loosening the assertion.

## 2026-08-19 Merging split regulations: 86% to 97%

Regulation 123 is now a single chunk containing all three ratios rather
than two chunks split at a page break. Four questions that had been
failing passed after the change.

Full progression: 73% baseline, 83% (TOP_K 5 to 8), 86% (carry regulation
number across page breaks), 28-29/29 (merge split regulations). 566 chunks
extracted, 342 after merging.

Every gain came from retrieval quality. The model and the prompt were
never the problem, and I would have wasted the whole phase tuning prompts
without the evals to point at retrieval.

## 2026-08-19 Eval scores have variance

The single failing question in one run passed when run again in isolation,
with the same retrieved chunks. The model had summarised more tightly
during the eval run and omitted elements it included the second time.
Three runs gave 28, 29, 29.

A single eval run is a sample, not a measurement. Quoting one number as
though it were stable overstates the precision, and a change that moves
the score by one question has told me nothing. Reporting a range.

## 2026-08-19 The eval set is now saturated

At 28-29 out of 29 the set can no longer detect improvement, and a drop of
one is indistinguishable from noise. A suite that everything passes has
stopped being a measurement.

Deferred rather than fixed. When it matters, the additions are harder
cases: questions needing two regulations combined, questions where a
jurisdictional variant overrides the base rule, and questions with a false
premise that should be corrected rather than answered.

## 2026-08-19 A 503 is not a ClientError

The retry logic caught errors.ClientError, which covers 429, and a
transient 503 fell straight through and killed the run. Both retry paths
now handle ServerError on 500, 502, 503 and 504 as well, with a shorter
backoff since server errors usually clear in seconds.