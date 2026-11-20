---
name: "doc-digest"
description: "Use when the user shares a long tech spec, design doc, requirements doc or proposal (file, Notion link or URL) and wants to understand it and give feedback or sign-off on it: brief, consistency check, stress-test questions, review comments, decision."
---

# Doc digest

For long, dense, often AI-written specs and proposals that the user has to understand and review. The reader's attention is the scarce resource, so every output here must be much shorter than what it replaces. Never answer a long document with a second long document.

Reply in the language the user writes in. Keep identifiers, names, ticket IDs, quotes and the draft review comments in the document's own language.

Work one step at a time. After each step stop and wait; move on when the user says so ("дальше", "next") or names a step.

## Files

Keep one review folder per document, next to the reading ledger:

- `reading-ledger.md` in the working directory: the ledger. Its first lines state the reader's seat and team.
- `YYYY-MM-DD-<slug>/doc.md`: the document as received. Never edit it.
- `YYYY-MM-DD-<slug>/brief.md`: the output of Steps 1 and 2.
- `YYYY-MM-DD-<slug>/notes.md`: the user's annotations and answers, saved as they arrive.
- `YYYY-MM-DD-<slug>/comments.md`: the output of Step 5, a paste sheet for Notion comments.

If the user passes a path, use that file's folder. If they pass a Notion link and a Notion connector is available, fetch the page and save it as `doc.md` in a new folder. If no file tools are available, print each output in the reply instead.

## Before you start

- Read the whole document, tables and appendices included. If the same document was given twice, say so and treat it as one.
- Know the reader's seat: which team they are on, and whether for this document they approve, are consulted, or are only informed. Take it from the first lines of the ledger. If it is missing, ask once and write it there.
- Read the ledger. It lists the people, systems, tickets and decisions the user already knows from earlier documents.

## Step 1: Brief (about 25 lines, one screen)

Write to `brief.md` and show it.

1. **What is asked of you, and by when.** The decision, sign-off or input the document wants from the reader, with the deadline. If the deadline has passed, say so first.
2. **The claim in three sentences.** What is proposed and why.
3. **Before and after.** What changes compared with today, as a short list.
4. **Cast.** People, teams, systems and ticket IDs with a one-line role each. Mark the ones that are new compared with the ledger; list known ones by name only.
5. **Numbers and dates that carry the argument.**
6. **Reading map.** Each section tagged read closely / skim / skip for this reader's seat, with a few words on why. This is the part that saves the most time; be decisive.

## Step 2: Check

Append to `brief.md`. Do the mechanical verification that people do badly on a long text:

- Recount every stated total, re-do the arithmetic, compare dates. Report what checks out in one line, so the reader need not spend attention on it.
- Find statements in different sections that contradict each other or silently describe different states (now versus later). Quote both places with their section names.
- Compare with the ledger: say where this document disagrees with what earlier documents stated.
- List what the document itself marks as unverified, assumed, open or to be decided.
- Name what a document of this kind should cover and this one does not (failure modes, rollback, ownership, cost, who is affected, dates).

Label each finding as *stated in the text* or *my inference*. If there is nothing to report under a heading, say so rather than padding. Rank by how much it matters to the reader's seat.

Then tell the user to read the sections marked "read closely". If they use plannotator, give the command: `/plannotator-annotate <path to doc.md>`.

## Step 3: Read together

The user reads and annotates in their own tool. Their annotations may arrive as a message with plannotator feedback (selected text with a comment, deletions, labels, "looks good" marks, a global comment) or as an `annotations.md` file. Save them to `notes.md`. They are the user's own notes and take priority over your findings.

- A comment starting with `Q:` is a question for the author, `Fix:` a requested change, `Blocker:` a blocker.
- A "looks good" mark means the passage was checked; do not raise it again.

Answer the user's questions briefly, point to the section, quote the relevant line. When the document does not answer the question, say that plainly and note it as a candidate review comment. Do not fill gaps with guesses about the author's intent.

## Step 4: Defend the document (offer it; skip if declined)

The user answers as if they were the author, using only what the document says. Ask six questions, one at a time, one from each pattern, each aimed at the highest-risk part of this document:

1. **Failure.** What happens when X fails?
2. **Alternative.** What did the alternative look like, and why was it rejected?
3. **Falsifiability.** How would we know this is wrong?
4. **Reversibility.** What does it cost to undo?
5. **Worst case.** Walk through the worst case.
6. **Trade-off.** Which quality does this sacrifice?

After each answer, classify it in one or two lines:

- answered from the text: confirm and name the section;
- the text answers it but the user did not: point to the section (a gap in understanding);
- the text does not answer it: record it in `notes.md` as a candidate comment (a gap in the document).

Never answer on the author's behalf. The question patterns follow the design-critique skill (psenger/ai-agent-skills).

## Step 5: Feedback and decision

Write `comments.md`. Draft review comments from the user's notes first, then from the Step 2 and Step 4 findings the user agreed with. At most seven, ranked. Write them short and in the user's voice, as a colleague would.

`comments.md` is a paste sheet: the user highlights the anchor in Notion and pastes the body as a comment. Give each comment its own section:

- a heading: the number and the issue as a short claim;
- `Severity: <blocker / should fix / question / nit>`, with the timing if it matters (e.g. "before the first app promotion"). This line is for the user, outside the pasted text;
- `Explanation:` in the language the user writes in, three to six sentences, for the user only. Say what the comment is about in plain words, with one concrete example of what goes wrong. Point to where the document says it (section and a short quote, plus the line in `doc.md`). Say what in the document comes closest to answering it, if anything, and how strong the comment is: a real gap, or a request to write down a reason. Explain any term from the document a newcomer would stumble on. Write it so the user can discuss the comment without asking you to explain it again;
- `Select in <section>: <anchor>`: a short phrase copied exactly from the document, which appears in it exactly once and contains no link. If the document came from Notion and a Notion connector is available, check each anchor against the live page, since it may have changed since `doc.md` was saved;
- the body in a ```` ```text ```` block, as one plain paragraph of two to four sentences and at most about 60 words, ending on the ask. The body carries no severity label and no timing advice. Notion comments render inline text only, so write identifiers as plain words, with no lists, headings or Markdown.

Write each body the way a colleague talks in a review thread: first what you saw, then why it matters to the reader's team or to production, then one concrete question or suggested change. Use plain words and short sentences, and say "I" and "we". Keep the author's own terms for things, so they recognise their design.

Keep it terse. The author wrote the document and the anchor shows the passage, so leave out anything the document already says. Each comment makes one point and carries one ask. Keep only the fact the author lacks and the detail needed to act on the ask; one example is enough. If the point still needs more words, cut the supporting detail, not the point, and move that detail to `notes.md` for the user to add in a reply.

Then run the `humanizer` skill over the comment bodies only. Afterwards check that each body still has its point, its ask, and the identifiers the ask needs. Restore anything that was lost, and keep the body within the word limit. If `humanizer` isn't installed, apply the two paragraphs above yourself.

End with a decision section, which is not for pasting: approve, approve with conditions, or not yet. Split conditions into "before approval" and "after approval, with an owner and a date". The decision is the user's: propose one only if asked, and say what it rests on.

Post a comment to Notion, GitHub or anywhere else only after the user's explicit go-ahead naming which comments to post, and only if the connector can create comments. Otherwise the user pastes them from `comments.md`.

## Step 6: Ledger

Append five to ten lines to `reading-ledger.md`: date, title, author; what was asked and by when; new people, systems and tickets; the user's position; open questions the user wants to track. If no ledger file is reachable, print the entry so the user can keep it.
