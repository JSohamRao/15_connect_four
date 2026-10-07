from board import Board, COLS


class AI:
    def choose_column(self, board, me="O", opponent="X"):
        # Break ties by proximity to the centre, where more winning lines cross.
        legal = sorted(board.legal_columns(), key=lambda c: (abs(c - COLS // 2), c))
        if not legal:
            return None

        # Win first; otherwise stop the opponent's immediate win.
        for token in (me, opponent):
            for col in legal:
                if self._after_move(board, col, token).winner(token):
                    return col

        # Avoid supplying support for an opponent's winning disc above ours.
        for col in legal:
            future = self._after_move(board, col, me)
            if not any(
                self._after_move(future, reply, opponent).winner(opponent)
                for reply in future.legal_columns()
            ):
                return col
        return legal[0]

    @staticmethod
    def _after_move(board, col, token):
        # Analyse a copy so speculative moves never change the live board.
        future = Board()
        future.grid = [row[:] for row in board.grid]
        future.drop(col, token)
        return future
