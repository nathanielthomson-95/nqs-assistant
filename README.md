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

## Licence

MIT