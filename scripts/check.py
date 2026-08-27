#!/usr/bin/env python3
"""Validate the standalone Apollo VS Code theme repository."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PALETTE_SHA256 = "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef"
HEX = re.compile(r"^#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?$")


def fail(message: str) -> None:
    raise AssertionError(message)


def walk_colors(value: Any, path: str = "") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(walk_colors(child, f"{path}.{key}" if path else key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_colors(child, f"{path}[{index}]"))
    elif isinstance(value, str) and value.startswith("#"):
        found.append((path, value))
    return found


def main() -> int:
    palette_path = ROOT / "palette" / "apollo.json"
    digest = hashlib.sha256(palette_path.read_bytes()).hexdigest()
    if digest != PALETTE_SHA256:
        fail(f"palette snapshot differs from canonical SHA-256: {digest}")

    palette = json.loads(palette_path.read_text(encoding="utf-8"))
    theme = json.loads((ROOT / "themes" / "apollo-color-theme.json").read_text(encoding="utf-8"))
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"], cwd=ROOT, check=True)

    if package.get("publisher") != "apollo-theme":
        fail("publisher must be the unclaimed organization-compatible placeholder 'apollo-theme'")
    if package.get("repository", {}).get("url") != "https://github.com/apollo-theme/vscode-apollo-theme.git":
        fail("package repository URL is incorrect")
    if package.get("contributes", {}).get("themes", [{}])[0].get("path") != "./themes/apollo-color-theme.json":
        fail("package does not contribute the generated Apollo theme")

    colors = theme["colors"]
    terminal = palette["terminal"]
    ansi_names = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")
    ansi = [colors[f"terminal.ansi{name}"] for name in ansi_names]
    bright = [colors[f"terminal.ansiBright{name}"] for name in ansi_names]
    if ansi != terminal["ansi"] or bright != terminal["bright"]:
        fail("integrated terminal arrays do not exactly match the palette")
    if colors["editor.foreground"] != "#cfbc97" or colors["focusBorder"] != "#fabd2f":
        fail("required foreground/accent mappings are missing")
    statuses = {
        "editorError.foreground": "#fb4934",
        "editorWarning.foreground": "#fabd2f",
        "editorInfo.foreground": "#83a598",
        "testing.iconPassed": "#b8bb26",
    }
    for key, expected in statuses.items():
        if colors.get(key) != expected:
            fail(f"semantic status {key} must be {expected}")

    restricted = [(path, color) for path, color in walk_colors(theme) if color.lower() == "#665c54"]
    if restricted != [("colors.terminal.ansiBrightBlack", "#665c54")]:
        fail(f"#665c54 is restricted to ANSI bright black, found: {restricted}")
    invalid = [(path, color) for path, color in walk_colors(theme) if not HEX.fullmatch(color)]
    if invalid:
        fail(f"invalid hex colors: {invalid}")
    if len(colors) < 150:
        fail(f"workbench theme is incomplete: only {len(colors)} color keys")
    if not theme.get("semanticHighlighting") or len(theme.get("semanticTokenColors", {})) < 20:
        fail("semantic highlighting coverage is incomplete")
    if len(theme.get("tokenColors", [])) < 25:
        fail("TextMate scope coverage is incomplete")

    print(
        f"validated palette snapshot, {len(colors)} workbench/terminal colors, "
        f"{len(theme['tokenColors'])} TextMate rules, and {len(theme['semanticTokenColors'])} semantic rules"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
