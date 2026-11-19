# Output formats

Three files. The lesson file is new per lesson; the dictionary and transcriptions files are shared across lessons and grow by one `## Lesson N` section each time.

Language: explanations, headings and translations in Russian; phrases, examples and exercises in English exactly as on the board.

---

## lesson-N.md

```markdown
# Lesson N — шпаргалка

Тема: <одна строка о теме урока>. Фразы и примеры взяты с доски урока.

---

## Task 1. <Название с доски> — <короткое пояснение по-русски>

<Короткая фраза о том, зачем это нужно, если она помогает.>

| Функция | Зачем | Фразы | Пример |
|---|---|---|---|
| **Opinion / stance** — мнение | ... | I would argue that… · It seems to me that… | I would argue that ... |

---

## Task 2. ...
```

Guidance, learned from the user's edits on earlier lessons:

- One `##` section per Task, in board order, titled `Task N. <board title> — <Russian gloss>`. Lesson material that sits outside a numbered Task (a language bank, grammar box) gets its own `##` section with the board's title.
- Prefer tables when the board has a type → purpose → phrases → example structure; bullet lists for plain phrase banks; a blockquote for a model paragraph labelled `**Пример …:**`.
- Scales and gradations get a value column (e.g. modals: might/may ~30%, could ~50%, should ~80%, must ~100%).
- Exercises: write the sentences with the correct answer filled in **bold**. Where another answer is also natural, add it right after in italics: `**As a result** *(или Consequently / Therefore)*`. If the board already shows the learner's answers, use the correct answer, not theirs.
- A short "Тонкости употребления" bullet list is welcome when the material has grammar traps (e.g. despite + noun vs although + clause).
- Leave out: margin vocabulary (→ dictionary.md), transcriptions (→ transcriptions.md), the learner's drafts and mistakes, duplicate second samples, and any meta-commentary such as "мои варианты", "сверьте с преподавателем", "на доске этого нет". Caveats go in the chat reply instead.

---

## dictionary.md

```markdown
# Dictionary

Слова и выражения с полей доски, по урокам.

---

## Lesson 1

| Слово / выражение | Перевод |
|---|---|
| lean towards | склоняться к |
| The game isn't worth a candle. | Игра не стоит свеч. |
```

- Source: words and phrases the teacher wrote in the margins or next to blocks (handwritten notes, highlighted words, Russian glosses). A Russian gloss written on the board is the translation to use.
- Append a new `## Lesson N` section, preceded by `---`. If that lesson's section already exists, replace only that section.

---

## transcriptions.md

```markdown
# Transcriptions

Транскрипции с доски, по урокам.

---

## Lesson 1

| Слово | Транскрипция |
|---|---|
| worth | /wɜːθ/ |

Звук **th**: they, these, this, think, thought, with. Не путать с **s**: think ≠ sink.
```

- Source: IPA written on the board. Copy it as written (fix only obvious OCR damage, using the standard dictionary IPA as a check). Pronunciation notes for that lesson (minimal pairs, sound drills) go under the table.
- Same append/replace rule as the dictionary.
