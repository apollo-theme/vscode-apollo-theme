# Apollo Theme for VS Code

This is a standalone VS Code color-theme extension. `palette/apollo.json` is an exact canonical snapshot; never hand-edit `themes/apollo-color-theme.json` or substitute colors from older local extensions.

## Commands

- Install dependencies: `npm ci`
- Regenerate: `npm run generate`
- Determinism and repository checks: `npm run check`
- All tests: `npm test`
- One named test: `python3 -m unittest tests.test_theme.VSCodeThemeTests.test_terminal_arrays_match_palette`
- Build VSIX: `npm run package`

## Invariants

- Generate all theme colors from `palette/apollo.json`.
- Keep foreground `#cfbc97`, accent/cursor/focus `#fabd2f`, and semantic status colors mapped to their canonical roles.
- Integrated-terminal normal and bright arrays must exactly equal the palette arrays.
- `#665c54` is allowed only as `terminal.ansiBrightBlack`, never normal editor or interface text.
- The publisher is an organization-compatible placeholder; do not claim Marketplace publication.
- Do not publish, install over a user's existing extension, or edit user settings while validating.
