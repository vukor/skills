# Example: triage and brief

A full Step 0 reply and the `brief.md` that follows it, for a fictional PR `acme/billing-service#412` ("fix: round invoice totals half-even"). Use it for shape and length, not content.

## Step 0 reply

- **Size:** 6 files, +142 / −38. 2 files are logic, 3 are tests, 1 is a regenerated OpenAPI client (mechanical, 61 lines).
- **Surface:** every invoice total. Rounding changes the amount customers are charged by up to one cent per line.
- **Reversibility:** a revert restores the old rounding, but invoices issued in between keep the new totals.

**Recommended path: Full.** It changes money for every customer, and issued invoices can't be taken back. It is not part of a stack.

Say "next" for the brief.

## brief.md

```markdown
# acme/billing-service#412 — fix: round invoice totals half-even

1. **Claim and ask.** Switches invoice rounding from half-up to half-even. You are asked to approve; your approval merges it.
2. **Description against diff.**
   - Matches: `round_total()` now uses `ROUND_HALF_EVEN`.
   - No code behind: "no customer-visible change" — totals ending in .5 cents change.
   - Not mentioned: `tax.py` also switches rounding mode.
3. **What changes.** Totals ending in exactly half a cent round to the even cent. Finance reports compare against the old totals.
4. **Reading map.**
   - Logic: `billing/rounding.py` — read closely; `billing/tax.py` — read closely
   - Tests: `tests/test_rounding.py` — read closely; `tests/test_tax.py`, `tests/fixtures/invoices.json` — skim
   - Mechanical: `clients/openapi/billing.py` — skip (regenerated)
5. **Who can answer.** The author, `@reviewer`; finance owns the reporting impact.

HTML: `pr-reviews/billing-service/pr-412/2026-01-12-explain.html` (Step 1b)
```
