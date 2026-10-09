# Fat Belly Hobo

A pure-frontend HTML5 street brawler game starring **Belly Bell** — a fat-bellied hobo fighting through 7 stages from San Francisco to Seattle.

## Play

Open `index.html` in a browser, or play at the GitHub Pages URL.

- **Touch controls**: on-screen buttons (jump, punch, kick, fart, spit, belly bash)
- **Keyboard**: arrows/WASD to move, I = fart (back), U = spit (front)

## Cheat codes

Tap the small **QA** button on the title screen, enter a code:

- `314` — stage select (jump to any of the 7 stages)
- `141421` — ultra-easy mode (full run, boosted stats)

## Tech

- Pure frontend, no backend, no build step
- Phaser 3.90.0 for character rendering (local copy in `assets/`)
- All art drawn procedurally in code (no external sprites)

## Tests

Automated external test suite (Playwright, deterministic, no product changes):
see `tests/` (coming soon).
