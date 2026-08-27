from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate  # noqa: E402


class VSCodeThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.palette_path = ROOT / "palette" / "apollo.json"
        cls.palette = json.loads(cls.palette_path.read_text(encoding="utf-8"))
        cls.theme_path = ROOT / "themes" / "apollo-color-theme.json"
        cls.theme = json.loads(cls.theme_path.read_text(encoding="utf-8"))

    def test_palette_snapshot_is_canonical(self) -> None:
        digest = hashlib.sha256(self.palette_path.read_bytes()).hexdigest()
        self.assertEqual(
            digest,
            "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef",
        )

    def test_generated_theme_is_current(self) -> None:
        self.assertEqual(self.theme_path.read_text(encoding="utf-8"), generate.render_theme(self.palette))

    def test_terminal_arrays_match_palette(self) -> None:
        colors = self.theme["colors"]
        ansi_keys = [
            "terminal.ansiBlack",
            "terminal.ansiRed",
            "terminal.ansiGreen",
            "terminal.ansiYellow",
            "terminal.ansiBlue",
            "terminal.ansiMagenta",
            "terminal.ansiCyan",
            "terminal.ansiWhite",
        ]
        bright_keys = [key.replace("terminal.ansi", "terminal.ansiBright") for key in ansi_keys]
        self.assertEqual([colors[key] for key in ansi_keys], self.palette["terminal"]["ansi"])
        self.assertEqual([colors[key] for key in bright_keys], self.palette["terminal"]["bright"])
        self.assertEqual(colors["terminal.foreground"], "#cfbc97")
        self.assertEqual(colors["terminalCursor.foreground"], "#fabd2f")

    def test_restricted_color_is_only_bright_black(self) -> None:
        found: list[str] = []

        def visit(value: object, path: str) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    visit(child, f"{path}.{key}" if path else key)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    visit(child, f"{path}[{index}]")
            elif isinstance(value, str) and value.lower() == "#665c54":
                found.append(path)

        visit(self.theme, "")
        self.assertEqual(found, ["colors.terminal.ansiBrightBlack"])

    def test_semantic_and_textmate_coverage(self) -> None:
        semantic = self.theme["semanticTokenColors"]
        for token in ("class", "function", "keyword", "number", "property", "string", "variable.readonly"):
            self.assertIn(token, semantic)

        scopes = {
            scope
            for rule in self.theme["tokenColors"]
            for scope in (rule["scope"] if isinstance(rule["scope"], list) else [rule["scope"]])
        }
        for scope in ("comment", "entity.name.function", "entity.name.type", "keyword.control", "markup.heading", "string"):
            self.assertIn(scope, scopes)

    def test_workbench_coverage(self) -> None:
        colors = self.theme["colors"]
        required = {
            "activityBar.background",
            "button.background",
            "diffEditor.insertedTextBackground",
            "editor.background",
            "editorError.foreground",
            "editorGutter.addedBackground",
            "input.background",
            "list.activeSelectionBackground",
            "menu.background",
            "notificationCenter.border",
            "panel.background",
            "peekView.border",
            "sideBar.background",
            "statusBar.background",
            "tab.activeBackground",
            "terminal.background",
            "titleBar.activeBackground",
        }
        self.assertTrue(required.issubset(colors), sorted(required - colors.keys()))
        self.assertGreaterEqual(len(colors), 150)


if __name__ == "__main__":
    unittest.main()
