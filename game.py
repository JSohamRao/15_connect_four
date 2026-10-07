from board import Board, COLS
from ai import AI


class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.turn = "X"

    def run(self):
        print("Connect Four — you are X.")
        self.board.print()
        if self._finished():
            return
        while True:
            if self.turn == "X":
                try:
                    raw = input(f"Column (1-{COLS}), or q: ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\nGame ended.")
                    return
                if raw == "q":
                    print("Game ended.")
                    return
                try:
                    col = int(raw) - 1
                except ValueError:
                    print("Enter a column number.")
                    continue
            else:
                col = self.ai.choose_column(self.board)

            row = self.board.drop(col, self.turn)
            if row is None:
                print("Column unavailable.")
                if self.turn == "O":
                    return
                continue

            print(f"{self.turn} placed a disc in column {col + 1}.")
            self.board.print()
            if self._finished():
                return

            self.turn = "O" if self.turn == "X" else "X"

    def _finished(self):
        for token in ("X", "O"):
            if self.board.winner(token):
                print(token, "wins!")
                return True
        if self.board.full():
            print("Draw.")
            return True
        return False
