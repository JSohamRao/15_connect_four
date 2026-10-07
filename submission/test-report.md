# Connect Four verification

Date: 7 October 2026. Executed using Python 3.12 on Windows.

## Before implementation

Original source: upstream commit `3347913`.

| Check | Observed result |
| --- | --- |
| Horizontal four | `True` |
| Vertical four | `True` |
| Rising diagonal four | `False` — defect reproduced |
| Falling diagonal four | `False` — defect reproduced |
| Game flow after diagonal four | AI moved again; another player prompt appeared |

The diagonal position used zero-based columns
`0, 1, 1, 2, 6, 2, 2, 3, 6, 3, 5, 3, 3`, alternating X/O.
For the game demonstration, the first 12 moves prepared the board, then X entered
column `4` (one-based). The before and after demonstrations use this same position
and final move. The falling diagonal was also reproduced by mirroring the columns.

Three baseline automated games covered immediate quitting, invalid input plus a
valid move, and several alternating turns with the original random AI.

## After implementation

Command: `python -m unittest discover -s tests -v`

Result: **26 tests passed**. See [captured output](test-results.txt).

| Requirement | Verification |
| --- | --- |
| All winning directions | All 69 possible four-cell windows for each of X/O; 138 winning positions |
| Shorter lines do not win | One, two and three discs in all four directions for both tokens |
| Gravity and full columns | Returned row order, rejected seventh drop, unchanged board |
| Invalid moves | Invalid types, ranges, tokens and console text leave state unchanged |
| Draws | Full draw fixture and final-cell draws after either player |
| Immediate game termination | No subsequent input or AI call after a terminal move |
| AI wins and blocks | Tactical checks in horizontal, vertical and both diagonal directions |
| AI legality | Full board, one legal column, excluded full columns |
| AI analysis | No output, no mutation; win-before-block and unsafe-support avoidance |
| Move feedback | Exactly one message per real drop; none for rejected inputs |
| Quitting | q, uppercase/whitespace q, EOF and Ctrl+C |
| Entry point | Real subprocess runs with quitting, invalid input, moves and EOF |

Both MP4s decode successfully and have a duration of exactly 10.00 seconds at
1280×800, 20 fps, H.264. Their captured program output is genuine; the presentation
is a rendered terminal replay, not a desktop recording. Inputs and board setup
are automated and explicitly labelled. No manual gameplay recording is claimed.

The original four-module structure is retained. `requirements.txt` remains
standard-library-only. No game persistence or database was added.
