"""Export hand-written quiz questions (JSON) to Moodle XML.

Usage:
    python build_tools/export_moodle_questions.py QUIZ.json [QUIZ.json ...] OUTPUT_DIR

QUIZ.json:
    {"category": "scikit-learn MOOC/Workbooks/Workbook M1.01",
     "name_prefix": "WB M1.01",
     "questions": [
        {"type": "single" | "multi", "text": "markdown",
         "options": [{"text": "markdown", "correct": true}, ...],
         "feedback": "markdown shown after the attempt"},
        {"type": "numerical", "text": "markdown", "answer": 0.31,
         "tolerance": 0.01, "feedback": "..."}
     ]}

Writes OUTPUT_DIR/<QUIZ>.xml for each file and OUTPUT_DIR/all_workbook_quizzes.xml
with all of them, to import in one go. The JSON files contain the
answers: keep them out of the public repository.
"""

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_moodle_quizzes import cdata, fraction, option_html, to_html  # noqa: E402

COMMON = """    <generalfeedback format="html"><text>{feedback}</text></generalfeedback>
    <defaultgrade>1</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber>{idnumber}</idnumber>
"""


def multichoice(q, name, idnumber):
    single = q["type"] == "single"
    correct = [o for o in q["options"] if o.get("correct")]
    if not correct or (single and len(correct) != 1):
        raise ValueError(f"{idnumber}: wrong number of correct options")
    n, k = len(q["options"]), len(correct)
    hint = "Select a single answer" if single else "Select all answers that apply"
    answers = []
    for o in q["options"]:
        if single:
            grade = 100 if o.get("correct") else 0
        elif o.get("correct"):
            grade = 100 / k
        else:
            grade = -100 / (n - k) if n > k else 0
        answers.append(
            f'    <answer fraction="{fraction(grade)}" format="html">\n'
            f"      <text>{cdata(option_html(o['text']))}</text>\n"
            f'      <feedback format="html"><text></text></feedback>\n'
            f"    </answer>"
        )
    text = to_html(q["text"]) + f"\n<p><em>{hint}</em></p>"
    return f"""  <question type="multichoice">
    <name><text>{html.escape(name)}</text></name>
    <questiontext format="html"><text>{cdata(text)}</text></questiontext>
{COMMON.format(feedback=cdata(to_html(q.get("feedback", ""))), idnumber=idnumber)}    <single>{'true' if single else 'false'}</single>
    <shuffleanswers>1</shuffleanswers>
    <answernumbering>abc</answernumbering>
    <showstandardinstruction>0</showstandardinstruction>
    <shownumcorrect/>
{chr(10).join(answers)}
  </question>
"""


def numerical(q, name, idnumber):
    return f"""  <question type="numerical">
    <name><text>{html.escape(name)}</text></name>
    <questiontext format="html"><text>{cdata(to_html(q["text"]))}</text></questiontext>
{COMMON.format(feedback=cdata(to_html(q.get("feedback", ""))), idnumber=idnumber)}    <answer fraction="100">
      <text>{q["answer"]}</text>
      <tolerance>{q.get("tolerance", 0)}</tolerance>
      <feedback format="html"><text></text></feedback>
    </answer>
    <unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
  </question>
"""


HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<quiz>\n'
FOOTER = "</quiz>\n"


def export(path, out_dir):
    """Write the quiz to its own file and return its XML body."""
    quiz = json.loads(path.read_text())
    out = [
        f'  <question type="category">\n    <category><text>$course$/top/'
        f'{html.escape(quiz["category"])}</text></category>\n  </question>\n',
    ]
    for i, q in enumerate(quiz["questions"], start=1):
        name = f"{quiz['name_prefix']} - Q{i:02d}"
        idnumber = f"{path.stem}_q{i:02d}"
        build = numerical if q["type"] == "numerical" else multichoice
        out.append(build(q, name, idnumber))
    body = "".join(out)
    target = out_dir / f"{path.stem}.xml"
    target.write_text(HEADER + body + FOOTER, encoding="utf-8")
    print(f"{path.name}: {len(quiz['questions'])} questions -> {target}")
    return body


if __name__ == "__main__":
    *paths, out_dir = sys.argv[1:]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bodies = [export(Path(p), out_dir) for p in sorted(paths)]
    combined = out_dir / "all_workbook_quizzes.xml"
    combined.write_text(HEADER + "".join(bodies) + FOOTER, encoding="utf-8")
    print(f"combined -> {combined}")
