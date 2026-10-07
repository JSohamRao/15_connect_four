# Scenario 15 — Connect Four vs AI

A terminal Connect Four game with a board module, a player turn loop, and a simple AI.

## Provided files

- `main.py` — entry point.
- `game.py` — turn handling and game flow.
- `board.py` — board state, drops, and win detection.
- `ai.py` — computer move selection.
- `requirements.txt` — dependency declaration.

## Setup

```bash
python main.py
```

## Before changing the code

Play several games, inspect all modules, and construct horizontal, vertical, and
diagonal winning positions. Trace how a move travels from the command line to the
board and then to winner detection.

## Task 1 — Complete win detection

Make win detection recognise every four-in-a-row direction, including both diagonals,
without breaking horizontal and vertical wins.

**Done when:** all four directions are detected and shorter sequences do not count.

## Task 2 — Complete game termination

Handle draws, full columns, invalid moves, and game termination consistently. A
winning move must stop the game before another turn is requested.

**Done when:** no invalid move changes the board and every terminal state is clear.

## Task 3 — Improve the AI

Add meaningful decision-making. The AI should take an immediate winning move when one
exists and block an immediate player win when necessary. Handle full columns safely.

**Done when:** the AI never selects an illegal column and responds correctly to one-move threats.

## Task 4 — Move-level feedback

Add concise feedback for a successful disc placement. It should occur once per actual
move, not once per cell inspected by win detection or AI analysis.

## Required testing

Test horizontal, vertical, both diagonals, draw positions, full columns, invalid input,
immediate AI wins, immediate AI blocks, and quitting.


## LLM usage

You may use an LLM during the lab. The goal is to use it as a coding assistant while
retaining responsibility for understanding and testing the result.

- Inspect the existing code before asking for changes.
- Ask for explanations when you do not understand a proposed change.
- Test generated code against the stated behaviour and edge cases.
- Keep your complete LLM chat history for submission.
- Do not replace the whole project with an unrelated implementation.
- Keep all state in memory; do not add CSV, JSON, SQLite, or other persistence.

## Submission checklist

- [x] Task 1 completed and the original defect was reproduced and fixed.
- [x] Tasks 2–4 completed and tested.
- [x] Boundary and invalid-input cases tested.
- [x] No unnecessary external dependencies added.
- [x] No persistent storage added.
- [x] Code remains understandable and modular.
- [ ] Complete LLM chat-history link included.

## Folder structure

```text
scenario-03-connect-four/
├── README.md
├── requirements.txt
├── main.py
├── game.py
├── board.py
└── ai.py
```

## Submission Checklist

Submission is only the following three things:

- [x] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [x] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history

## Implementation notes

The original defect was reproduced at upstream commit `3347913`: horizontal and
vertical wins were detected, but both diagonals returned `False`. A diagonal
winning move also allowed an extra AI move and another player prompt. Before
editing, three automated game sessions exercised quitting, invalid input and
ordinary alternating moves; all four winning directions were constructed.

- `board.py` checks horizontal, vertical and both diagonal directions. Invalid
  columns or tokens and full columns return `None` without changing the grid.
  `legal_columns()` exposes the available moves.
- `game.py` handles wins and draws before another turn, rejects invalid input
  without advancing the turn, and ends cleanly on `q`, EOF or Ctrl+C. It prints
  one placement message for each successful real move.
- `ai.py` tries an immediate win first, then blocks an immediate opponent win.
  Otherwise it favours the centre and avoids moves that support an immediate
  opponent win. Analysis uses copied boards and produces no placement messages.
  A full board yields `None`; every other selected column is legal. This is a
  tactical AI, and positions with multiple independent threats can still be lost.

The move flow remains `main.py` → `Game.run()` → `Board.drop()` → placement
feedback → `Board.winner()` / `Board.full()` → next turn if play can continue.
The game uses only Python's standard library and keeps its entire state in memory.

## Verification

From the repository directory:

```bash
python main.py
python -m unittest discover -s tests -v
```

The automated suite contains **26 passing tests**, covering every required case:
all four win directions at every valid boundary for both tokens, shorter lines,
legal-drop diagonal positions, full columns, invalid input, draws after either
player's final move, terminal-state handling, AI wins and blocks in all four
directions, win-before-block priority, legal AI moves, unchanged live state during
analysis, once-per-move feedback, quitting, EOF and Ctrl+C. The entry point is
also exercised in real subprocesses.

The [test report](submission/test-report.md) and
[captured test output](submission/test-results.txt) provide execution evidence.

## Submission files

- [Before gameplay video — 10 seconds](submission/before.mp4)
- [After gameplay video — 10 seconds](submission/after.mp4)
- [Chat-history link status](submission/chat-history.md) — pending; add the
  complete conversation link before academic submission.

The videos are labelled terminal **output replays**, rendered from genuine
captured program output with automated input. They are not desktop screen
recordings. Demo positions were prepared with legal alternating drops; the real
game loop and AI were used. The before output was captured before editing. The
after video demonstrates the fixed diagonal, an AI block and an AI win. An
isolated recording utility used Pillow and FFmpeg outside this repository; the
game, tests and demo runner need no external dependencies. Saved submission
evidence is not game-state persistence.

To reproduce the after demonstrations:

```bash
python tools/demo.py diagonal
python tools/demo.py block
python tools/demo.py win
```

To reproduce the original bug in an isolated checkout, without changing the
completed working tree:

```bash
git worktree add ../connect-four-before 3347913
python tools/demo.py diagonal --source ../connect-four-before
```
