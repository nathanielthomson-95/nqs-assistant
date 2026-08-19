# nqs-assistant
Compliance assistant for Australian childcare regulation. In development
#NQS Assistant

A compliance assistant for Australian early childhood education and care services. Ask a plain-language question, get an answer with a citation back to the exact regulation or standard.

## The problem

Centre directors and nominated supervisors are responsible for compliance with the Education and Care Services National Law and Regulations, and with the seven quality areas of the National Quality Standard. In practice this means several hundred pages of cross-referencing legislation.

The questions that come up are usually specific and urgent. What is the ratio for this age group in this state. Does this qualification count towards it. What has to be documented and for how long. Answering them means knowing which document to open and where to look in it, which is knowledge held by experienced directors and not much help to anyone else.

Searching the source documents is difficult because the answer to a practical question is often spread across a regulation, a guideline and a state-specific variation.

## Who is it for

Centre directors, nominated supervisors and educational leaders, particularly in smaller services without a compliance team behind them.

## What it does

- Answers plain-language compliance questions
- Cites the specific regulations or NQS element behind every answer
- Says clearly when the source documents do not contain an answer, rather than guessing

## Approach

Retrieval augmented generation over the source documents, rather than a fine tuned model. In a compliance context the citation matters as much as the answer, and retrieval makes the source traceable. A confident but unsourced anser is worse than no answer.

## Status

In development. Building in phases: API and data layer, then retrieval and evaluation, then a web interface, then deployment.

## Planned stack

Python, FastAPI, PostgreSQL with pgvector, TypeScript, React

## Planned structure

app/
    main.py # app creation and router registration
    config.py # Settings from environment
    database.py # engine, session, dependancy
    models.py # database tables
    schemas.py # request and response models
    routers/ # endpoint definitions
    services/ # retrieval, model calls, business logic
tests/
evals/ # question set and scoring script

## Tests

![tests](https://github.com/nathanielthomson-95/nqs-assistant/actions/workflows/tests.yml/badge.svg)

## Results

Retrieval accuracy: 28 to 29 of 29 eval questions, up from 22 at baseline.

The eval set covers ratios, space requirements, record keeping,
qualifications, notification timeframes and policies, plus four questions
the source documents cannot answer, which the system is expected to
decline rather than answer from training data.

Expected answers were verified against the source document rather than
against the system's own output. Improvements came from retrieval quality
rather than prompting:

| Change | Score |
|---|---|
| Baseline | 22/29 |
| Retrieve 8 chunks rather than 5 | 24/29 |
| Carry regulation numbers across page breaks | 25/29 |
| Merge regulations split across pages | 28-29/29 |

Scores vary by a question or two between runs, so the final figure is
given as a range. The set is now saturated and would need harder cases to
measure further change.

## Licence

MIT
