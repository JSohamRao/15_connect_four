ROWS, COLS = 6, 7


class Board:
    def __init__(self):
        self.grid = [["."] * COLS for _ in range(ROWS)]

    def drop(self, col, token):
        if type(col) is not int or not 0 <= col < COLS or token not in ("X", "O"):
            return None
        for r in range(ROWS - 1, -1, -1):
            if self.grid[r][col] == ".":
                self.grid[r][col] = token
                return r
        return None

    def full(self):
        return all(self.grid[0][c] != "." for c in range(COLS))

    def legal_columns(self):
        return [c for c in range(COLS) if self.grid[0][c] == "."]

    def winner(self, token):
        if token not in ("X", "O"):
            return False
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] != token:
                    continue
                for dr, dc in directions:
                    if all(
                        0 <= r + i * dr < ROWS and
                        0 <= c + i * dc < COLS and
                        self.grid[r + i * dr][c + i * dc] == token
                        for i in range(4)
                    ):
                        return True
        return False

    def print(self):
        print("\n  " + " ".join(str(i + 1) for i in range(COLS)))
        for row in self.grid:
            print("  " + " ".join(row))
