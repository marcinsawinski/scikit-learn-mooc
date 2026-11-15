"""Build one starter notebook per wrap-up quiz.

Usage:
    python build_tools/build_quiz_notebooks.py

The wrap-up quizzes (jupyter-book/**/*wrap_up_quiz*.md) require programming.
For each of them this writes quiz_notebooks/<quiz>.ipynb with the code the
quiz gives (loading the dataset, defining a model...) ready to run, so that
students can open it in Google Colab from the quiz page. The notebooks only
contain what is already on the quiz page: no answers.

The script also makes sure each quiz page shows the "Open in Colab" badge
under its "requires some programming" line. Run it again after editing the
code blocks of a wrap-up quiz.
"""

import re
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

GITHUB_REPO = "marcinsawinski/scikit-learn-mooc"
GITHUB_BRANCH = "main"
REPO_DIR = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_DIR / "jupyter-book"
OUT_DIR = REPO_DIR / "quiz_notebooks"
RAW_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/{GITHUB_BRANCH}/"
)
BOOK_URL = "https://marcinsawinski.github.io/scikit-learn-mooc/"
INTRO_LINE = "**This quiz requires some programming to be answered.**"
BADGE_MARK = "<!-- colab-badge -->"

QUESTION = re.compile(r"^```\{admonition\} Question")
CODE_START = re.compile(r"^```py(thon)?\s*$")


def colab_link(notebook_name):
    return (
        f"https://colab.research.google.com/github/{GITHUB_REPO}/blob/"
        f"{GITHUB_BRANCH}/quiz_notebooks/{notebook_name}"
    )


def badge(notebook_name):
    return (
        f'<a href="{colab_link(notebook_name)}" target="_blank" rel="noopener">'
        '<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        'alt="Open In Colab"/></a>'
    )


def given_code(text):
    """Code blocks of the quiz page, with the question they come before."""
    blocks, n_questions, current = [], 0, None
    for line in text.splitlines():
        if current is not None:
            if line.strip() == "```":
                blocks.append((n_questions + 1, "\n".join(current)))
                current = None
            else:
                current.append(line)
        elif CODE_START.match(line):
            current = []
        elif QUESTION.match(line):
            n_questions += 1
    return blocks


def build_notebook(quiz_path):
    text = quiz_path.read_text()
    title = re.search(r"^# (.+)$", text, flags=re.MULTILINE).group(1).strip()
    page = quiz_path.relative_to(BOOK_DIR).with_suffix(".html").as_posix()
    cells = [
        new_markdown_cell(
            f"# {title} — starter notebook\n\n"
            f"Use this notebook to answer the questions of the "
            f"[{title}]({BOOK_URL}{page}).\n\n"
            "Run the code given at the start of the quiz, then add your own "
            "cells to answer the questions. Code that the quiz gives later "
            "is included further down, where you will need it."
        )
    ]
    your_work_added = False
    for before_question, code in given_code(text):
        if before_question > 1 and not your_work_added:
            cells.append(new_markdown_cell("**Your work**"))
            cells.append(new_code_cell(""))
            your_work_added = True
        if before_question == 1:
            label = "**Code given at the start of the quiz**"
        else:
            label = (
                f"**Code given before question {before_question}.** It may use "
                "what you wrote for the earlier questions: run it when you "
                "get there."
            )
        cells.append(new_markdown_cell(label))
        code = re.sub(r"(\.\./)+datasets/", RAW_URL + "datasets/", code)
        cells.append(new_code_cell(code))
    if not your_work_added:
        cells.append(new_markdown_cell("**Your work**"))
        cells.append(new_code_cell(""))

    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    for cell in nb.cells:
        cell.pop("id", None)
    nb.nbformat_minor = 4
    return nb


def add_badge(quiz_path, notebook_name):
    """Show the badge under the intro line of the quiz page (idempotent)."""
    text = quiz_path.read_text()
    block = (
        f"{BADGE_MARK}\n{badge(notebook_name)}\n\n"
        "The notebook behind this badge already contains the code given "
        "below."
    )
    if BADGE_MARK in text:
        # Replace the existing block: the badge paragraph and its sentence.
        start = text.index(BADGE_MARK)
        end = text.index("\n\n", text.index("\n\n", start) + 2)
        text = text[:start] + block + text[end:]
    elif INTRO_LINE in text:
        text = text.replace(INTRO_LINE, f"{INTRO_LINE}\n\n{block}", 1)
    else:
        raise ValueError(f"{quiz_path}: intro line not found")
    quiz_path.write_text(text)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    for quiz_path in sorted(BOOK_DIR.glob("*/*wrap_up_quiz*.md")):
        notebook_name = f"{quiz_path.stem}.ipynb"
        nbformat.write(build_notebook(quiz_path), OUT_DIR / notebook_name)
        add_badge(quiz_path, notebook_name)
        print(f"{quiz_path.relative_to(REPO_DIR)} -> quiz_notebooks/{notebook_name}")
