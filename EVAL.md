# Retrieval evaluation

This document describes what `scripts/eval_retrieval.py` measures, the current result, and what it does **not** prove.

## What the probe measures

Lexora's RAG path has two separable failure modes: retrieving the wrong chunks, and generating an unsupported answer. This probe tests only the first, and only its cheapest precondition: **can a chunk containing the answer be found by keyword overlap at all?**

For each case, the script:

1. Chunks the document with `TextChunker` (recursive splitting at paragraph, sentence, and word boundaries, 1,000-character ceiling).
2. Tokenizes the question into lowercase alphanumeric terms and removes a small English stop-word list.
3. Scores every chunk by the number of question terms it contains.
4. Checks whether the answer span appears in any of the top-k chunks.

It needs no OpenAI key, no database, and no network, so it runs in CI and on a fresh clone.

## Current result

Run on `main` on 2026-11-18:

```text
PASS refund_policy: 2 chunks, top-3 contains 'support@example.com'
PASS rate_limits: 1 chunks, top-3 contains '429'
PASS postgres_setup: 2 chunks, top-3 contains 'alembic upgrade head'

recall@3: 3/3
```

| Case | Question | Expected span | Chunks | Result |
|---|---|---|---:|---|
| `refund_policy` | How do I request a refund? | `support@example.com` | 2 | pass |
| `rate_limits` | What happens when I exceed the rate limit? | `429` | 1 | pass |
| `postgres_setup` | How do I run database migrations? | `alembic upgrade head` | 2 | pass |

The script exits non-zero on any miss, so a chunking regression that separates an answer from its surrounding context fails the check rather than silently lowering quality.

## How to run it

```bash
python scripts/eval_retrieval.py
python scripts/eval_retrieval.py --top-k 5
```

## Why keyword recall is the right floor

Semantic retrieval can only return a chunk that exists. If the chunker splits `alembic upgrade head` away from the migration instructions, or buries the refund address in an unrelated chunk, no embedding model will recover it reliably. Fixing chunking is free; re-embedding a corpus is not. A pipeline that fails this probe should not be evaluated on generation quality yet.

## What it does not measure

- **Semantic recall.** Keyword overlap is a proxy. A chunk that repeats the question's words but does not answer it can rank highly.
- **Answer faithfulness.** The probe never calls the LLM, so it says nothing about hallucination or citation accuracy.
- **Ranking quality beyond top-k.** There is no MRR, nDCG, or per-query score distribution.
- **Real documents.** The three cases are short synthetic policy and API documents. They exercise chunk boundaries, not messy PDFs, tables, or multi-column layouts.
- **Scale.** Three cases cannot detect a regression that affects one document type in a hundred.

This is a smoke test with a clear pass/fail, not a benchmark. It should not be quoted as retrieval accuracy in a paper or a résumé line.

## Next steps

1. Replace the synthetic cases with 30–50 real question/answer pairs from actual uploaded documents, each with a labelled supporting chunk.
2. Report recall@k for k = 1, 3, 5 and MRR; keep the current probe as a fast CI gate.
3. Add an embedding-based retrieval comparison once the labelled set exists, so keyword and semantic retrieval can be compared on the same cases.
4. Evaluate generation separately: citation correctness (does the cited chunk contain the claim?) and answer faithfulness, with an LLM judge plus periodic human review.
5. Record latency and cost per query alongside quality so retrieval changes are judged on the full trade-off.
