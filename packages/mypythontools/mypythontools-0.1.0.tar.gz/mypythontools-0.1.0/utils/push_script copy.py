"""Push the CI pipeline. Format, create commit from all the changes, push and deploy to PyPi."""

import os
import inspect
from pathlib import Path
import sys

import subprocess

subprocess.run(
    [
        "python",
        "utils/push_script.py",
        "--test",
        "True",
        "--deploy",
        "False",
        "--reformat",
        "False",
        "--commit_and_push_git",
        "False",
        "--sphinx_docs",
        "False",
    ]
)
