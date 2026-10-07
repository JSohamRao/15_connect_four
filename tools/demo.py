"""Run reproducible gameplay demonstrations using the real Game and AI modules.

Positions are prepared using legal drops; input is automated and echoed.
There is no saved game state and no replacement AI.
"""
import argparse
from pathlib import Path
import sys
from unittest.mock import patch


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scene", choices=("diagonal", "block", "win"))
parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1], help="Directory containing the game modules")
args = parser.parse_args()
sys.path.insert(0, str(args.source.resolve()))

from game import Game


game = Game()
if args.scene == "diagonal":
    moves = [0, 1, 1, 2, 6, 2, 2, 3, 6, 3, 5, 3]
    inputs = iter(["4", "q"])
elif args.scene == "block":
    moves = [0, 6, 1, 6]
    inputs = iter(["3", "q"])
else:
    moves = [0, 6, 1, 6, 0, 6, 1]
    game.turn = "O"
    inputs = iter([])

for index, col in enumerate(moves):
    assert game.board.drop(col, "X" if index % 2 == 0 else "O") is not None
assert not game.board.winner("X") and not game.board.winner("O")


def enter(prompt):
    value = next(inputs)
    print(prompt + value)
    return value


with patch("builtins.input", enter):
    game.run()
