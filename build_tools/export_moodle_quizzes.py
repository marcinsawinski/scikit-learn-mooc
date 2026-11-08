"""Export the Jupyter Book quizzes to Moodle XML.

Usage:
    python build_tools/export_moodle_quizzes.py ANSWER_KEY.json OUTPUT_DIR

ANSWER_KEY.json maps each question id (see parse_quizzes.py) to
{"correct": ["a", ...], "confidence": "high|medium|low", "rationale": "..."}.

Writes one Moodle XML file per quiz, a combined all_quizzes.xml, and
answer_key_review.md listing every answer for the teacher to check.

Questions are multiple choice. For "select all that apply" questions, each
correct option is worth 100/k % (k correct options) and each wrong option
-100/(n-k) %; Moodle never lets a question score go below 0. Questions whose
answer was marked medium/low confidence get the "answer-needs-review" tag.

The answer key and generated files contain the solutions: keep them out of
the public repository.
"""

import html
import json
import re
import sys
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_quizzes import BOOK_DIR, parse_quiz, quiz_files  # noqa: E402

GITHUB_REPO = "marcinsawinski/scikit-learn-mooc"
GITHUB_BRANCH = "main"
RAW_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}/"
)
TOP_CATEGORY = "scikit-learn MOOC"

# Grades Moodle accepts for a multiple choice answer, in %.
MOODLE_FRACTIONS = [
    100, 90, 83.33333, 80, 75, 70, 66.66667, 60, 50, 40, 33.33333, 30, 25, 20,
    16.66667, 14.28571, 12.5, 11.11111, 10, 5, 0,
]

md = MarkdownIt("commonmark").enable("table").use(
    dollarmath_plugin, allow_digits=False
)
md.add_render_rule(
    "math_inline", lambda self, tokens, idx, options, env: (
        "\\(" + html.escape(tokens[idx].content) + "\\)"
    )
)
md.add_render_rule(
    "math_block", lambda self, tokens, idx, options, env: (
        "<p>\\[" + html.escape(tokens[idx].content) + "\\]</p>\n"
    )
)


def fraction(value):
    """Closest grade Moodle accepts, keeping the sign."""
    best = min(MOODLE_FRACTIONS, key=lambda f: abs(f - abs(value)))
    text = str(int(best)) if best == int(best) else repr(best)
    return text if value >= 0 or best == 0 else "-" + text


def preprocess(text):
    """MyST/relative-path bits that plain Markdown does not understand."""
    # ```{note} ... ``` -> blockquote
    def note(m):
        body = "\n".join("> " + line for line in m.group(1).strip().splitlines())
        return "> **Note**\n>\n" + body

    text = re.sub(r"```\{note\}\n(.*?)\n```", note, text, flags=re.DOTALL)
    text = re.sub(r"(\.\./)+figures/", RAW_URL + "figures/", text)
    text = re.sub(r"(\.\./)+datasets/", RAW_URL + "datasets/", text)
    return text


def to_html(text):
    return md.render(preprocess(text)).strip() if text.strip() else ""


def option_html(text):
    out = to_html(text)
    # A single paragraph does not need <p> around it.
    m = re.fullmatch(r"<p>(.*)</p>", out, flags=re.DOTALL)
    if m and "<p>" not in m.group(1):
        out = m.group(1)
    return out


def cdata(text):
    return "<![CDATA[" + text.replace("]]>", "]]]]><![CDATA[>") + "]]>"


def module_captions():
    """Map quiz path (without .md) -> numbered table of contents caption."""
    captions, current, n = {}, None, 0
    for line in (BOOK_DIR / "_toc.yml").read_text().splitlines():
        m = re.match(r"- caption: (.+)", line)
        if m:
            n += 1
            name = re.sub(r"^[^\w]+", "", m.group(1)).strip()
            current = f"{n:02d} {name}"
        m = re.search(r"file: (\S+)", line)
        if m and current:
            captions[m.group(1).removesuffix(".md")] = current
    return captions


def clean_title(title):
    return re.sub(r"^[^\w]+", "", title).strip()


def question_xml(quiz, q, answer, module):
    title = clean_title(quiz["title"])
    labels = [o["label"] for o in q["options"]]
    correct = answer["correct"]
    unknown = set(correct) - set(labels)
    if unknown or not correct:
        raise ValueError(f"{q['id']}: invalid answer {correct} for {labels}")
    if q["single"] and len(correct) != 1:
        raise ValueError(f"{q['id']}: single answer question with {correct}")

    hint = "Select a single answer" if q["single"] else "Select all answers that apply"
    parts = []
    if q["context"]:
        parts.append(f'<div class="quiz-context">{to_html(q["context"])}</div>')
    parts.append(to_html(q["stem"]))
    if q["trailer"]:
        parts.append(to_html(q["trailer"]))
    parts.append(f"<p><em>{hint}</em></p>")
    text = "\n".join(parts)

    n, k = len(labels), len(correct)
    answers = []
    for o in q["options"]:
        if q["single"]:
            grade = 100 if o["label"] in correct else 0
        elif o["label"] in correct:
            grade = 100 / k
        else:
            grade = -100 / (n - k) if n > k else 0
        answers.append(
            f'    <answer fraction="{fraction(grade)}" format="html">\n'
            f"      <text>{cdata(option_html(o['text']))}</text>\n"
            f"      <feedback format=\"html\"><text></text></feedback>\n"
            f"    </answer>"
        )

    tags = [quiz["module"]]
    if answer.get("confidence") != "high":
        tags.append("answer-needs-review")
    tags_xml = "".join(f"<tag><text>{html.escape(t)}</text></tag>" for t in tags)

    # Quiz titles are reused across modules (e.g. "Quiz M4.01" in linear
    # models and clustering): prefix the module to keep names unique.
    name = f"{module}: {title} - Q{q['number']:02d}"
    return f"""  <question type="multichoice">
    <name><text>{html.escape(name)}</text></name>
    <questiontext format="html"><text>{cdata(text)}</text></questiontext>
    <generalfeedback format="html"><text></text></generalfeedback>
    <defaultgrade>1</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>{html.escape(q['id'])}</idnumber>
    <single>{'true' if q['single'] else 'false'}</single>
    <shuffleanswers>0</shuffleanswers>
    <answernumbering>abc</answernumbering>
    <showstandardinstruction>0</showstandardinstruction>
    <correctfeedback format="html"><text></text></correctfeedback>
    <partiallycorrectfeedback format="html"><text></text></partiallycorrectfeedback>
    <incorrectfeedback format="html"><text></text></incorrectfeedback>
    <shownumcorrect/>
{chr(10).join(answers)}
    <tags>{tags_xml}</tags>
  </question>
"""


def category_xml(path):
    return f"""  <question type="category">
    <category><text>$course$/top/{html.escape(path)}</text></category>
  </question>
"""


def quiz_xml(quiz, key, captions):
    quiz_path = quiz["source"].removeprefix("jupyter-book/").removesuffix(".md")
    category = f"{TOP_CATEGORY}/{captions[quiz_path]}/{clean_title(quiz['title'])}"
    out = [category_xml(category)]
    for q in quiz["questions"]:
        if q["id"] not in key:
            raise KeyError(f"No answer for {q['id']}")
        module = captions[quiz_path].split(" ", 1)[1]
        out.append(question_xml(quiz, q, key[q["id"]], module))
    return "".join(out)


def wrap(body):
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n{body}</quiz>\n'


def review_markdown(quizzes, key, captions):
    lines = [
        "# Answer key review",
        "",
        "Generated answer key. Questions marked ⚠️ have medium or low",
        "confidence and are tagged `answer-needs-review` in Moodle.",
        "",
    ]
    for quiz in quizzes:
        quiz_path = quiz["source"].removeprefix("jupyter-book/").removesuffix(".md")
        lines += [f"## {captions[quiz_path]} / {clean_title(quiz['title'])}", "",
                  f"Source: `{quiz['source']}`", ""]
        for q in quiz["questions"]:
            a = key[q["id"]]
            flag = "" if a.get("confidence") == "high" else " ⚠️"
            options = {o["label"]: o["text"].replace("\n", " ") for o in q["options"]}
            stem = q["stem"].replace("\n", " ")
            lines.append(f"### Q{q['number']:02d}{flag} `{q['id']}`")
            lines.append("")
            lines.append(stem)
            lines.append("")
            for label, text in options.items():
                mark = "✅" if label in a["correct"] else "▫️"
                lines.append(f"- {mark} {label}) {text}")
            lines.append("")
            lines.append(f"**Confidence:** {a.get('confidence')}  ")
            lines.append(f"**Why:** {a.get('rationale', '')}")
            if a.get("computed"):
                lines.append(f"  \n**Computed:** {a['computed']}")
            lines.append("")
    return "\n".join(lines)


def main(answer_key_path, out_dir):
    key = json.loads(Path(answer_key_path).read_text())
    quizzes = [parse_quiz(p) for p in quiz_files()]
    captions = module_captions()
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    expected = {q["id"] for quiz in quizzes for q in quiz["questions"]}
    extra = set(key) - expected
    if extra:
        raise KeyError(f"Answers for unknown questions: {sorted(extra)}")

    combined = []
    for quiz in quizzes:
        body = quiz_xml(quiz, key, captions)
        (out_dir / f"{quiz['quiz_id']}.xml").write_text(wrap(body), encoding="utf-8")
        combined.append(body)
    (out_dir / "all_quizzes.xml").write_text(wrap("".join(combined)), encoding="utf-8")
    (out_dir / "answer_key_review.md").write_text(
        review_markdown(quizzes, key, captions), encoding="utf-8"
    )
    n = len(expected)
    review = sum(1 for k in expected if key[k].get("confidence") != "high")
    print(f"{len(quizzes)} quizzes, {n} questions, {review} tagged for review -> {out_dir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
