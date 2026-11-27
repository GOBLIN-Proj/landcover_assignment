"""The usage example (`tests/example.py`) runs, and the README shows it as it is.

The README's usage section is a copy of `tests/example.py`; if either changes without the other, this fails.
"""
import contextlib
import io
import re
import unittest

from _helpers import ROOT

import example


class Example(unittest.TestCase):
    def test_runs(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            example.main()
        text = out.getvalue()
        for heading in ("combined future land use area", "spared area log", "grassland area breakdown",
                        "transition matrix", "afforestation"):
            self.assertIn(heading, text)

    def test_readme_shows_the_example(self):
        readme = (ROOT / "README.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
        blocks = re.findall(r"```python\n(.*?)```", readme, flags=re.S)
        source = (ROOT / "tests/example.py").read_text(encoding="utf-8")
        self.assertIn(source, blocks)
