---
name: esp-lessons-extract
description: Turn a PDF export of a Miro (or similar whiteboard) English-lesson board into study notes for one lesson — a lesson-N.md cheat sheet, plus new sections appended to dictionary.md (margin vocabulary) and transcriptions.md (IPA from the board). Use whenever the user uploads a board/canvas PDF or PNG from their English teacher and asks to recognise it, make a шпаргалка / cheat sheet / конспект for "lesson 2", pull out phrases, words or transcriptions from a lesson, or add a lesson to their dictionary — even if they don't say "Miro" or name the files.
---

# Miro lesson → cheat sheet

The user learns English with a teacher who builds each lesson on a giant Miro board, then exports it to PDF. They want, for one lesson at a time, three Markdown files they keep and reread:

| File | What goes in | Mode |
|---|---|---|
| `lesson-N.md` | the lesson's Tasks as a compact cheat sheet | new file per lesson |
| `dictionary.md` | words/phrases the teacher wrote in the margins, with translations | append `## Lesson N` |
| `transcriptions.md` | IPA written on the board, plus sound drills | append `## Lesson N` |

The exact templates and style rules are in `references/formats.md` — read it before writing anything. They come from the user's own edits, so following them saves the user a round of corrections.

## Inputs

- The board PDF (required).
- Which lesson to extract (`lesson 2`, `the second lesson`, `урок 3`). If not given, ask — one board often holds several lessons.
- Existing `dictionary.md` / `transcriptions.md`, if the user has them. Look for them among attached files and in the working directory; if they aren't there, start new ones and say so in the reply, so the user knows to merge.

## Workflow

### 1. Prepare the board for reading

Miro PDFs are raster images (12 000+ px wide) with no text layer, so text has to be read from images. Run:

```bash
python3 <skill-dir>/scripts/extract_board.py "<board.pdf>" <scratch>/board
```

It writes full page images, overlapping tiles (low-resolution pages are upscaled ×3), an OCR draft per tile and `index.txt`. If the PDF does have a text layer (`pdftotext` returns real text), use that instead.

### 2. Find the lesson

Lessons are delimited by Task numbering, not by page: a lesson is the run of blocks titled `TASK 1`, `TASK 2`, … and a new `TASK 1` starts the next lesson. Tasks of one lesson can be spread over several pages, with homework or revision blocks in between — group by numbering. Unnumbered exercise blocks belong to the lesson whose Task they practise (a "Choose the most appropriate connector" block belongs with the Connectors task). "Home assignment" blocks are homework, not cheat-sheet material, unless the user asks for them.

Skim `ocr/page-*.txt` to map where each Task sits. If the boundary is ambiguous, pick the most reasonable reading and state it in one line in the reply.

### 3. Read it properly

OCR is a draft: it drops words at tile edges, mangles IPA, misreads Cyrillic and handwriting, and loses table structure. For every block you will use:

- Open the tile(s) with the Read tool and read the text yourself. When a block is cut by a tile edge, crop the page image around the block (PIL, from `page-N.png`) instead of guessing the missing part.
- Tell apart three kinds of text: teacher's material (printed blocks, tables, stickies), teacher's margin notes (loose words, Russian glosses, IPA, highlighted corrections) and the learner's own answers/drafts (often in yellow boxes or filled-in blanks, sometimes with red marks on errors). Only the first two go into the files; learner answers are not models.
- Never invent text that isn't legible. If a phrase is unreadable, drop it, or restore it only when the meaning is unambiguous, and mention it in the reply.

### 4. Write the files

Follow `references/formats.md`. In short:

- `lesson-N.md`: one section per Task in board order, tables where the board has structure, model paragraphs as `**Пример …:**` blockquotes, exercises with correct answers in bold and natural alternatives as `*(или …)*`. No meta-commentary inside the file — the user deleted every "мои варианты / сверьте с преподавателем" note; such caveats belong in the chat reply.
- `dictionary.md` and `transcriptions.md`: add (or replace) only the `## Lesson N` section; keep everything else untouched.

Exercise answers are yours, not the teacher's. Choose the answer a teacher would accept; where an exercise is internally inconsistent (e.g. "use each connector once" but one slot fits none), pick the natural answer and flag it in the reply.

### 5. Check and deliver

- Re-read the lesson file against the board tiles once: every phrase spelled as on the board, no learner drafts slipped in, no Task missing.
- Deliver all three files (SendUserFile or the environment's equivalent).
- Reply in Russian, briefly: which board part you took as Lesson N, then a short list of what to verify — answers you filled in, restored or uncertain phrases, anything left out. That list is where the caveats live.

## Why the rules look like this

The user rereads these files before speaking practice, so they want them dense and clean: only what the teacher taught, laid out for fast lookup. Vocabulary and transcriptions accumulate across lessons, which is why they live in separate growing files rather than inside each cheat sheet. Notes about uncertainty are useful once, at handover, but clutter the file forever — hence chat, not file.
