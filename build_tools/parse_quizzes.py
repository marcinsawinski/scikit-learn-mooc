"""Parse the Jupyter Book quiz pages into structured questions.

Each question keeps the markdown that precedes it since the previous question
(setup code, explanations, figures) as ``context``, because wrap-up quizzes
rely on it.
"""

import json
import re
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parent.parent / "jupyter-book"

QUESTION_START = re.compile(r"^(`{3,})\{admonition\}\s*Questions?\s*$")
OPTION = re.compile(r"^- ([a-z])\) ?(.*)$")
SELECT = re.compile(r"_Select (all answers that apply|a single answer)_")

# Module order follows the book table of contents.
MODULE_ORDER = [
    "ml_concepts",
    "predictive_modeling_pipeline",
    "overfit",
    "tuning",
    "linear_models",
    "trees",
    "ensemble",
    "evaluation",
    "clustering",
    "dimensionality",
    "feature_selection",
    "interpretation",
]


def quiz_files():
    toc = (BOOK_DIR / "_toc.yml").read_text()
    in_toc = re.findall(r"file: (\S*quiz\S*)", toc)
    files = [BOOK_DIR / f"{f.removesuffix('.md')}.md" for f in in_toc]
    others = sorted(set(BOOK_DIR.glob("*/*quiz*.md")) - set(files))
    return files + others


def clean_context(lines):
    text = "\n".join(l for l in lines if l.strip() != "+++").strip()
    return text


def split_question(body_lines):
    stem, options, trailer = [], [], []
    state = "stem"
    for line in body_lines:
        m = OPTION.match(line)
        if m and state in ("stem", "options"):
            state = "options"
            options.append({"label": m.group(1), "text": m.group(2)})
        elif state == "options" and line.strip():
            # Indented or lazy (unindented) continuation of the option.
            options[-1]["text"] += "\n" + line.removeprefix("  ")
        elif state == "options" and not line.strip():
            state = "after_options"
        elif state == "stem":
            stem.append(line)
        else:
            state = "trailer"
            trailer.append(line)
    trailer_text = "\n".join(trailer).strip()
    m = SELECT.search(trailer_text)
    single = m is not None and m.group(1) == "a single answer"
    trailer_text = SELECT.sub("", trailer_text).strip()
    for o in options:
        o["text"] = o["text"].strip()
    return "\n".join(stem).strip(), options, trailer_text, single, m is not None


def parse_quiz(path):
    lines = path.read_text().splitlines()
    title = None
    questions = []
    context = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if title is None and line.startswith("# "):
            title = line[2:].strip()
            i += 1
            continue
        m = QUESTION_START.match(line)
        if not m:
            context.append(line)
            i += 1
            continue
        fence = m.group(1)
        j = i + 1
        while lines[j].rstrip() != fence:
            j += 1
        stem, options, trailer, single, has_select = split_question(lines[i + 1 : j])
        number = len(questions) + 1
        questions.append(
            {
                "id": f"{path.stem}_q{number:02d}",
                "number": number,
                "context": clean_context(context),
                "stem": stem,
                "options": options,
                "trailer": trailer,
                "single": single,
                "has_select_hint": has_select,
            }
        )
        context = []
        i = j + 1
    trailing = clean_context(context)
    # Some quizzes put the "_Select ..._" hint right after the question block:
    # it then shows up at the start of the next question context.
    for k, q in enumerate(questions):
        following = questions[k + 1]["context"] if k + 1 < len(questions) else trailing
        m = SELECT.match(following)
        if m and not q["has_select_hint"]:
            q["single"] = m.group(1) == "a single answer"
            q["has_select_hint"] = True
            following = following[m.end():].strip()
            if k + 1 < len(questions):
                questions[k + 1]["context"] = following
            else:
                trailing = following
    return {
        "quiz_id": path.stem,
        "module": path.parent.name,
        "source": str(path.relative_to(BOOK_DIR.parent)),
        "title": title,
        "is_wrap_up": "wrap_up" in path.stem,
        "trailing_text": trailing,
        "questions": questions,
    }


if __name__ == "__main__":
    quizzes = [parse_quiz(p) for p in quiz_files()]
    out = Path(sys.argv[1])
    out.write_text(json.dumps(quizzes, indent=1, ensure_ascii=False))
    n = sum(len(q["questions"]) for q in quizzes)
    print(f"{len(quizzes)} quizzes, {n} questions -> {out}")
