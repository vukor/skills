# Example: page outline and one quiz question

The outline of a finished page for a fictional PR `acme/billing-service#412` ("fix: round invoice totals half-even"), plus one quiz question in full. Use it for structure, not content.

## Outline

1. **Table of contents**: links to the four sections.
2. **Background**
   - *For beginners (skip if familiar):* how floating-point and decimal amounts differ; what a rounding mode is.
   - *For this change:* where `round_total()` sits in the invoice pipeline, with a system diagram: order → line items → tax → total, each box showing a sample amount.
3. **Intuition**: one toy invoice with three lines ending in .5 cents, rounded half-up and half-even side by side. A callout defines "banker's rounding".
4. **Code**: in reading-map order: `billing/rounding.py`, then `billing/tax.py`, then the tests; each hunk in a `<pre>` block with two or three sentences on what it does.
5. **Quiz**: five multiple-choice questions.

## One quiz question

> An invoice line is 10.125. What does `round_total()` return after this change?
>
> - 10.13
> - **10.12** ✓
> - 10.1
> - It raises, because the amount has three decimals
>
> Feedback when 10.12 is picked: "Correct. Half-even rounds a tie to the even cent, and 2 is even."
> Feedback when 10.13 is picked: "That was the old half-up behaviour, replaced in `billing/rounding.py`."
