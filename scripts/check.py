#!/usr/bin/env python3
"""Validate both standalone Apollo VS Code theme variants."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PALETTE_SHA256 = {
    "apollo": "550f8c36cf4ef6ac99551541d1fe9554f77d563fa1e7c129a6a82583321d61ef",
    "apollo-light": "b0dbdeb719ed1931c424e9590562689325ecac1609e2fed6406ec5c4d3dc5763",
}
VARIANTS = (
    ("apollo", "dark", ROOT / "palette" / "apollo.json", ROOT / "themes" / "apollo-color-theme.json"),
    ("apollo-light", "light", ROOT / "palette" / "apollo-light.json", ROOT / "themes" / "apollo-light-color-theme.json"),
)
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


def validate_variant(variant_id: str, appearance: str, palette_path: Path, theme_path: Path) -> tuple[int, int, int]:
    digest = hashlib.sha256(palette_path.read_bytes()).hexdigest()
    if digest != PALETTE_SHA256[variant_id]:
        fail(f"{palette_path.relative_to(ROOT)} differs from canonical SHA-256: {digest}")

    palette = json.loads(palette_path.read_text(encoding="utf-8"))
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    if (palette.get("id"), palette.get("appearance")) != (variant_id, appearance):
        fail(f"{palette_path.name} has incorrect variant semantics")
    if (theme.get("name"), theme.get("type")) != (palette["name"], appearance):
        fail(f"{theme_path.name} has incorrect name/type semantics")

    colors = theme["colors"]
    terminal = palette["terminal"]
    ansi_names = ("Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White")
    ansi = [colors[f"terminal.ansi{name}"] for name in ansi_names]
    bright = [colors[f"terminal.ansiBright{name}"] for name in ansi_names]
    if ansi != terminal["ansi"] or bright != terminal["bright"]:
        fail(f"{theme_path.name} terminal arrays do not exactly match its palette")
    if colors["editor.foreground"] != palette["colors"]["foreground"]:
        fail(f"{theme_path.name} editor foreground is incorrect")
    if colors["focusBorder"] != palette["colors"]["accent"]:
        fail(f"{theme_path.name} focus color is incorrect")

    statuses = {
        "editorError.foreground": "danger",
        "editorWarning.foreground": "accent",
        "editorInfo.foreground": "info",
        "testing.iconPassed": "success",
    }
    for key, role in statuses.items():
        if colors.get(key) != palette["colors"][role]:
            fail(f"{theme_path.name} semantic status {key} must use {role}")

    invalid = [(path, color) for path, color in walk_colors(theme) if not HEX.fullmatch(color)]
    if invalid:
        fail(f"{theme_path.name} contains invalid hex colors: {invalid}")
    if len(colors) < 150:
        fail(f"{theme_path.name} is incomplete: only {len(colors)} color keys")
    if not theme.get("semanticHighlighting") or len(theme.get("semanticTokenColors", {})) < 20:
        fail(f"{theme_path.name} semantic highlighting coverage is incomplete")
    if len(theme.get("tokenColors", [])) < 25:
        fail(f"{theme_path.name} TextMate scope coverage is incomplete")
    return len(colors), len(theme["tokenColors"]), len(theme["semanticTokenColors"])


def main() -> int:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate.py"), "--check"], cwd=ROOT, check=True)
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))

    if package.get("publisher") != "apollo-theme":
        fail("publisher must remain 'apollo-theme'")
    if package.get("repository", {}).get("url") != "https://github.com/apollo-theme/vscode-apollo-theme.git":
        fail("package repository URL is incorrect")
    expected_contributions = [
        {"label": "Apollo", "uiTheme": "vs-dark", "path": "./themes/apollo-color-theme.json"},
        {"label": "Apollo Light", "uiTheme": "vs", "path": "./themes/apollo-light-color-theme.json"},
    ]
    if package.get("contributes", {}).get("themes") != expected_contributions:
        fail("package must contribute exactly Apollo/vs-dark and Apollo Light/vs")
    versions = (package.get("version"), lock.get("version"), lock.get("packages", {}).get("", {}).get("version"))
    if versions != ("0.2.0", "0.2.0", "0.2.0"):
        fail(f"package and lock versions must all be 0.2.0, got {versions}")

    counts = [validate_variant(*variant) for variant in VARIANTS]
    print(
        "validated two palette snapshots and theme variants; "
        + ", ".join(
            f"{variant[0]}={colors} colors/{textmate} TextMate/{semantic} semantic"
            for variant, (colors, textmate, semantic) in zip(VARIANTS, counts, strict=True)
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"check failed: {error}", file=sys.stderr)
        raise SystemExit(1)
