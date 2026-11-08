"""Build student workbooks from their solution source.

Usage:
    python build_tools/build_workbooks.py SOLUTIONS_DIR STUDENT_DIR EXECUTED_SOLUTIONS_DIR

Each solution is a jupytext "percent" Python file. Gaps for students are lines
of the form

    name = <python literal>  # BLANK

Lines ending with ``# VERIFY`` (assertions recomputing an answer from the
data) are kept in the solution only. In the student notebook the value becomes ``____``. When the solution also
calls ``check("name", name)``, the expected value is stored as a hash in the
notebook so students get immediate feedback without seeing the answer.
The ``GAP_HELPERS`` placeholder is replaced by the helper code.

The solution notebooks are executed, so every ``check`` is verified against
the real data before the student version is written.
"""

import ast
import hashlib
import json
import re
import sys
from pathlib import Path

import jupytext
import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_markdown_cell

GITHUB_REPO = "marcinsawinski/scikit-learn-mooc"
GITHUB_BRANCH = "main"
REPO_DIR = Path(__file__).resolve().parent.parent

BLANK = re.compile(r"^(?P<indent>\s*)(?P<name>\w+) = (?P<value>.+?)\s+# BLANK\s*$")
CHECK = re.compile(r'check\("(\w+)"')

# Shared between the build (to hash answers) and the notebook (to check them).
NORMALIZE_SRC = '''
def _normalize(value):
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, float):
        value = round(value, 2)
    if isinstance(value, (list, tuple, set)):
        return ",".join(sorted(str(v).strip().lower() for v in value))
    return str(value).strip().lower()


def _hash(value):
    return hashlib.sha256(_normalize(value).encode()).hexdigest()[:16]
'''

HELPERS_TEMPLATE = '''import hashlib
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

ANSWERS = {answers}
{normalize}

def check(name, value):
    """Stop with a hint unless `value` is the expected answer for `name`."""
    if _hash(value) != ANSWERS[name]:
        raise ValueError(
            f"❌ {{name}} = {{value!r}} is not right. "
            "Re-read the text above this cell and try again."
        )
    print(f"✅ {{name}}")


def commit(prediction, options):
    """Record a prediction before seeing the result."""
    if prediction not in options:
        raise ValueError(f"Choose one of {{options}} first.")
    print(f"📌 Your prediction: {{prediction!r}}. Now run the next cell and compare.")
'''

namespace = {"hashlib": hashlib}
exec(NORMALIZE_SRC, namespace)
_hash = namespace["_hash"]


def split(source):
    blanks, student_lines, solution_lines = {}, [], []
    for line in source.splitlines():
        m = BLANK.match(line)
        if line.rstrip().endswith("# VERIFY"):
            # Solution-only assertion recomputing an answer from the data.
            solution_lines.append(line)
        elif m:
            blanks[m["name"]] = ast.literal_eval(m["value"])
            student_lines.append(f"{m['indent']}{m['name']} = ____")
            solution_lines.append(f"{m['indent']}{m['name']} = {m['value']}")
        else:
            student_lines.append(line)
            solution_lines.append(line)
    return blanks, "\n".join(student_lines) + "\n", "\n".join(solution_lines) + "\n"


def with_helpers(source, answers):
    helpers = HELPERS_TEMPLATE.format(
        answers=json.dumps(answers, indent=4), normalize=NORMALIZE_SRC
    )
    return source.replace("GAP_HELPERS", helpers.strip())


def to_notebook(source, colab_path):
    nb = jupytext.reads(source, fmt="py:percent")
    badge = (
        f'<a href="https://colab.research.google.com/github/{GITHUB_REPO}/blob/'
        f'{GITHUB_BRANCH}/{colab_path}" target="_parent"><img '
        'src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open In Colab"/></a>'
    )
    nb.cells.insert(0, new_markdown_cell(badge))
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3", "language": "python", "name": "python3"
    }
    for cell in nb.cells:
        cell.pop("id", None)
    nb.nbformat_minor = 4
    return nb


def build(solution_path, student_dir, executed_dir):
    source = solution_path.read_text()
    blanks, student_src, solution_src = split(source)
    checked = set(CHECK.findall(source))
    missing = checked - set(blanks)
    if missing:
        raise KeyError(f"{solution_path.name}: check() without BLANK: {missing}")
    answers = {name: _hash(blanks[name]) for name in sorted(checked)}

    student_path = student_dir / f"{solution_path.stem}.ipynb"
    colab_path = student_path.resolve().relative_to(REPO_DIR).as_posix()

    solution_nb = to_notebook(with_helpers(solution_src, answers), colab_path)
    NotebookClient(solution_nb, timeout=600, kernel_name="python3").execute()
    nbformat.write(solution_nb, executed_dir / f"{solution_path.stem}.ipynb")

    student_nb = to_notebook(with_helpers(student_src, answers), colab_path)
    nbformat.write(student_nb, student_path)
    print(f"{solution_path.name}: {len(blanks)} gaps, {len(answers)} checked -> {student_path}")


if __name__ == "__main__":
    solutions_dir, student_dir, executed_dir = map(Path, sys.argv[1:4])
    student_dir.mkdir(parents=True, exist_ok=True)
    executed_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(solutions_dir.glob("*.py")):
        build(path, student_dir, executed_dir)
