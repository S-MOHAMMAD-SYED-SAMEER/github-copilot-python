import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def _is_valid_partial_board(board):
    for row in range(SIZE):
        values = [value for value in board[row] if value != EMPTY]
        if any(value < 1 or value > SIZE for value in values):
            return False
        if len(values) != len(set(values)):
            return False

    for col in range(SIZE):
        values = [board[row][col] for row in range(SIZE) if board[row][col] != EMPTY]
        if len(values) != len(set(values)):
            return False

    for start_row in range(0, SIZE, 3):
        for start_col in range(0, SIZE, 3):
            values = [
                board[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
                if board[row][col] != EMPTY
            ]
            if len(values) != len(set(values)):
                return False
    return True

def count_solutions(board, limit=2):
    if limit <= 0:
        return 0
    if not _is_valid_partial_board(board):
        return 0

    best_cell = None
    best_candidates = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                candidates = [
                    candidate
                    for candidate in range(1, SIZE + 1)
                    if is_safe(board, row, col, candidate)
                ]
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates

    if best_cell is None:
        return 1

    row, col = best_cell
    solutions = 0
    for candidate in best_candidates:
        board[row][col] = candidate
        solutions += count_solutions(board, limit - solutions)
        board[row][col] = EMPTY
        if solutions >= limit:
            return solutions
    return solutions

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    for row, col in positions:
        if sum(cell != EMPTY for row in board for cell in row) <= clues:
            break
        original = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = original

    return sum(cell != EMPTY for row in board for cell in row) == clues

def generate_puzzle(clues=35, difficulty=None):
    if difficulty is not None:
        try:
            clues = DIFFICULTY_CLUES[difficulty]
        except KeyError:
            raise ValueError('difficulty must be easy, medium, or hard')

    if not 0 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 0 and 81')

    for _ in range(100):
        board = create_empty_board()
        if not fill_board(board):
            continue
        solution = deep_copy(board)
        if remove_cells(board, clues):
            return deep_copy(board), solution

    raise RuntimeError('unable to generate a unique puzzle with the requested clues')
