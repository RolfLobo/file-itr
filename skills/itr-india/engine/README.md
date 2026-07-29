# itr-india tax engine

Deterministic, auditable Indian ITR computation engine. **Phase 1 (this build):**
input model + provenance-carrying rule-table + transaction-date-aware income
*bucketing* + audit trace + fail-loud scope. **No rate math, no set-off yet** —
those are Phases 2–3. Every statutory value is a `Rule` with a verified citation;
`buckets.py` classifies each income line into a tax-treatment bucket.

Run tests: `pytest skills/itr-india/engine/tests -v`
