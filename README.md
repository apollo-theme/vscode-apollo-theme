# Apollo Theme for Visual Studio Code

A complete warm, high-contrast dark theme generated from the canonical Apollo palette. It covers the workbench, editor, integrated terminal, Git/diff states, testing/debugging UI, TextMate scopes, and semantic tokens.

The package uses `apollo-theme` as an organization-compatible publisher placeholder and is **not** represented as published in the Visual Studio Marketplace.

## Install

### From a local VSIX

1. Run `npm ci`.
2. Run `npm run package`.
3. In VS Code, open **Extensions: Install from VSIX...** from the Command Palette.
4. Select `dist/apollo-theme.vsix`.

Alternatively, use an isolated VS Code profile so existing settings and extensions stay untouched:

```sh
code --user-data-dir /tmp/apollo-vscode-profile --extensions-dir /tmp/apollo-vscode-extensions --install-extension dist/apollo-theme.vsix
```

## Activate

Open **Preferences: Color Theme** and select **Apollo**. Choosing a theme changes VS Code's color-theme setting; use an isolated profile if you do not want to alter your normal profile.

## Uninstall

Open Extensions, locate **Apollo Theme**, select the gear menu, and choose **Uninstall**. From an isolated CLI profile:

```sh
code --user-data-dir /tmp/apollo-vscode-profile --extensions-dir /tmp/apollo-vscode-extensions --uninstall-extension apollo-theme.apollo-theme
```

Then delete the temporary profile/directories if used.

## Visual verification

Verify all of the following in VS Code:

- Editor canvas is near-black `#141617`; ordinary source text is warm `#cfbc97`.
- Active focus, cursor, active line number, and find matches use gold `#fabd2f`.
- Errors are red, warnings gold, information blue, and successful tests/Git additions green.
- Comments remain readable muted brown and `#665c54` is never used for normal text.
- JavaScript/TypeScript, Python, C#, JSON, CSS/HTML, Markdown, and diff views show distinct functions, types, properties, strings, constants, and markup.
- The integrated terminal renders the exact canonical normal and bright ANSI rows, including bright black only in its ANSI slot.

## Develop and validate

```sh
npm ci
npm run generate
npm run check
npm test
npm run package
```

Run one focused test with:

```sh
python3 -m unittest tests.test_theme.VSCodeThemeTests.test_terminal_arrays_match_palette
```

`themes/apollo-color-theme.json` is deterministic generated output. Change `scripts/generate.py` for mapping changes, then regenerate. `palette/apollo.json` is a fixed snapshot and must remain byte-for-byte canonical.

## License

MIT. Copyright (c) 2026 D0n9X1n.
