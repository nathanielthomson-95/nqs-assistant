Respend with JSON only. No prose before or after, no markdown fences.

Shape:
{
    "answer": "string, plain language, two or three sentences",
    "confidence": "high" | "medium" | "low",
    "clauses": ["string, e.g. Regulation 123 or NQS 4.1"],
    "caveat": "string or null, anything the reader should be careful about"
}

Use confidence "low" and an empty clause list when the context does not support a confident answer.