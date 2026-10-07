import contextlib
import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from ai import AI
from board import Board, COLS, ROWS
from game import Game


DIAGONAL_MOVES = [0, 1, 1, 2, 6, 2, 2, 3, 6, 3, 5, 3, 3]
DRAW_ROWS = ["XXOOXXO", "OOXXOOX"] * 3


def position(moves):
    board = Board()
    for index, col in enumerate(moves):
        assert board.drop(col, "X" if index % 2 == 0 else "O") is not None
    return board


def draw_board():
    board = Board()
    board.grid = [list(row) for row in DRAW_ROWS]
    return board


class BoardTests(unittest.TestCase):
    def test_every_direction_at_every_boundary_for_both_tokens(self):
        for token in ("X", "O"):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                for row in range(ROWS):
                    for col in range(COLS):
                        if not (0 <= row + 3 * dr < ROWS and 0 <= col + 3 * dc < COLS):
                            continue
                        with self.subTest(token=token, direction=(dr, dc), start=(row, col)):
                            board = Board()
                            for i in range(4):
                                board.grid[row + i * dr][col + i * dc] = token
                            self.assertTrue(board.winner(token))
                            self.assertFalse(board.winner("O" if token == "X" else "X"))

    def test_short_lines_in_all_directions_are_not_wins(self):
        for token in ("X", "O"):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                for length in (1, 2, 3):
                    board = Board()
                    for i in range(length):
                        board.grid[1 + i * dr][3 + i * dc] = token
                    with self.subTest(token=token, direction=(dr, dc), length=length):
                        self.assertFalse(board.winner(token))

    def test_diagonals_built_by_legal_drops(self):
        self.assertTrue(position(DIAGONAL_MOVES).winner("X"))
        self.assertTrue(position([6 - col for col in DIAGONAL_MOVES]).winner("X"))

    def test_empty_cells_and_invalid_tokens_are_not_winners(self):
        for token in (".", "", "Z", None):
            self.assertFalse(Board().winner(token))

    def test_drop_uses_gravity_and_rejects_full_column(self):
        board = Board()
        for row in reversed(range(ROWS)):
            self.assertEqual(board.drop(0, "X" if row % 2 else "O"), row)
        snapshot = [row[:] for row in board.grid]
        self.assertIsNone(board.drop(0, "X"))
        self.assertEqual(board.grid, snapshot)
        self.assertNotIn(0, board.legal_columns())

    def test_invalid_drop_leaves_board_unchanged(self):
        board = Board()
        for col in (-1, COLS, 100, None, "1", 1.5, True):
            with self.subTest(col=col):
                self.assertIsNone(board.drop(col, "X"))
                self.assertEqual(board.grid, Board().grid)
        for token in (".", "", "Z", None):
            self.assertIsNone(board.drop(0, token))
            self.assertEqual(board.grid, Board().grid)

    def test_full_draw_fixture_has_no_winner(self):
        board = draw_board()
        self.assertTrue(board.full())
        self.assertEqual(board.legal_columns(), [])
        self.assertFalse(board.winner("X"))
        self.assertFalse(board.winner("O"))


class AITests(unittest.TestCase):
    def setUp(self):
        self.ai = AI()

    def test_takes_immediate_wins_in_every_direction(self):
        self._check_tactical_moves("O")

    def test_blocks_immediate_threats_in_every_direction(self):
        self._check_tactical_moves("X")

    def _check_tactical_moves(self, token):
        for name in ("horizontal", "vertical", "rising", "falling"):
            board = Board()
            if name == "horizontal":
                for col in (0, 1, 2):
                    board.drop(col, token)
                expected = 3
            elif name == "vertical":
                for _ in range(3):
                    board.drop(6, token)
                expected = 6
            else:
                board = position(DIAGONAL_MOVES[:-1])
                if token == "O":
                    board.grid = [[{"X": "O", "O": "X", ".": "."}[cell] for cell in row] for row in board.grid]
                if name == "falling":
                    board.grid = [list(reversed(row)) for row in board.grid]
                # Remove an unrelated threat on the bottom row.
                board.grid[5][2] = token
                expected = 3
            with self.subTest(token=token, direction=name):
                snapshot = [row[:] for row in board.grid]
                self.assertEqual(self.ai.choose_column(board), expected)
                self.assertEqual(board.grid, snapshot)

    def test_win_has_priority_over_block(self):
        board = Board()
        for _ in range(3):
            board.drop(0, "X")
            board.drop(6, "O")
        self.assertEqual(self.ai.choose_column(board), 6)

    def test_handles_full_board(self):
        self.assertIsNone(self.ai.choose_column(draw_board()))

    def test_only_legal_column_is_chosen(self):
        board = draw_board()
        board.grid[0][6] = "."
        self.assertEqual(self.ai.choose_column(board), 6)

    def test_full_columns_are_ignored(self):
        board = Board()
        for _ in range(ROWS):
            board.drop(3, "X")
        self.assertIn(self.ai.choose_column(board), board.legal_columns())

    def test_opening_prefers_centre_without_output_or_mutation(self):
        board = Board()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(self.ai.choose_column(board), 3)
        self.assertEqual(board.grid, Board().grid)
        self.assertEqual(output.getvalue(), "")

    def test_avoids_supporting_an_opponents_win(self):
        board = Board()
        for col in (0, 1, 2):
            board.drop(col, "X" if col == 1 else "O")
            board.drop(col, "X")
        # Filling (5, 3) would enable X's horizontal win at (4, 3).
        self.assertNotEqual(self.ai.choose_column(board), 3)

    def test_configurable_tokens(self):
        board = Board()
        for _ in range(3):
            board.drop(0, "X")
        self.assertEqual(self.ai.choose_column(board, me="X", opponent="O"), 0)


class GameTests(unittest.TestCase):
    def run_game(self, game, inputs):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), patch("builtins.input", side_effect=inputs) as enter:
            game.run()
        return output.getvalue(), enter

    def test_invalid_input_and_ranges_do_not_move_or_call_ai(self):
        game = Game()
        game.ai.choose_column = Mock()
        output, _ = self.run_game(game, ["abc", "", "1.5", "0", "8", "-2", "q"])
        self.assertEqual(game.board.grid, Board().grid)
        game.ai.choose_column.assert_not_called()
        self.assertNotIn("placed a disc", output)
        self.assertEqual(output.count("Enter a column number."), 3)
        self.assertEqual(output.count("Column unavailable."), 3)

    def test_full_column_does_not_change_turn_or_board(self):
        game = Game()
        for index in range(ROWS):
            game.board.drop(0, "X" if index % 2 else "O")
        before = [row[:] for row in game.board.grid]
        game.ai.choose_column = Mock()
        output, _ = self.run_game(game, ["1", "q"])
        self.assertIn("Column unavailable.", output)
        self.assertEqual(game.board.grid, before)
        self.assertEqual(game.turn, "X")
        game.ai.choose_column.assert_not_called()

    def test_player_diagonal_win_stops_before_another_turn(self):
        game = Game()
        game.board = position(DIAGONAL_MOVES[:-1])
        game.ai.choose_column = Mock()
        output, enter = self.run_game(game, ["4"])
        self.assertIn("X wins!", output)
        self.assertEqual(enter.call_count, 1)
        game.ai.choose_column.assert_not_called()
        self.assertEqual(output.count("placed a disc"), 1)

    def test_ai_win_stops_without_player_input(self):
        game = Game()
        game.turn = "O"
        for _ in range(3):
            game.board.drop(6, "O")
        output, enter = self.run_game(game, [])
        self.assertIn("O wins!", output)
        self.assertIn("O placed a disc in column 7.", output)
        enter.assert_not_called()

    def test_feedback_occurs_once_per_real_move(self):
        game = Game()
        output, _ = self.run_game(game, ["1", "q"])
        self.assertEqual(output.count("X placed a disc"), 1)
        self.assertEqual(output.count("O placed a disc"), 1)
        self.assertEqual(sum(cell != "." for row in game.board.grid for cell in row), 2)

    def test_last_cell_causes_draw_before_ai_turn(self):
        game = Game()
        game.board = draw_board()
        game.board.grid[0][0] = "."
        game.ai.choose_column = Mock()
        output, enter = self.run_game(game, ["1"])
        self.assertIn("Draw.", output)
        self.assertNotIn("wins!", output)
        self.assertEqual(enter.call_count, 1)
        game.ai.choose_column.assert_not_called()

    def test_ai_can_fill_last_cell_and_draw(self):
        game = Game()
        game.turn = "O"
        game.board = draw_board()
        game.board.grid[0][2] = "."
        output, enter = self.run_game(game, [])
        self.assertIn("Draw.", output)
        self.assertEqual(output.count("placed a disc"), 1)
        enter.assert_not_called()

    def test_existing_terminal_boards_never_request_input(self):
        for winner in ("X", "O", None):
            game = Game()
            game.ai.choose_column = Mock()
            if winner is None:
                game.board = draw_board()
            else:
                for col in (0, 1, 2, 3):
                    game.board.drop(col, winner)
            output, enter = self.run_game(game, [])
            self.assertIn(f"{winner} wins!" if winner else "Draw.", output)
            enter.assert_not_called()
            game.ai.choose_column.assert_not_called()

    def test_quit_eof_and_interrupt_end_cleanly(self):
        for value in ("q", " Q ", EOFError(), KeyboardInterrupt()):
            game = Game()
            game.ai.choose_column = Mock()
            output, _ = self.run_game(game, [value])
            self.assertIn("Game ended.", output)
            self.assertEqual(game.board.grid, Board().grid)
            game.ai.choose_column.assert_not_called()

    def test_entry_point_handles_real_console_input(self):
        root = Path(__file__).resolve().parents[1]
        for raw in ("q\n", "invalid\n0\n8\n4\nq\n", ""):
            with self.subTest(input=raw):
                result = subprocess.run([sys.executable, "main.py"], input=raw, text=True, capture_output=True, cwd=root, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Game ended.", result.stdout)


if __name__ == "__main__":
    unittest.main()
