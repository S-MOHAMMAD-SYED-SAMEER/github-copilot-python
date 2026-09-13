import sudoku_logic
import pytest


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(row == [sudoku_logic.EMPTY] * sudoku_logic.SIZE for row in board)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert not sudoku_logic.is_safe(board, 0, 1, 1)
    assert not sudoku_logic.is_safe(board, 1, 0, 1)
    assert not sudoku_logic.is_safe(board, 1, 1, 1)
    assert sudoku_logic.is_safe(board, 1, 1, 2)


def test_generate_puzzle_returns_valid_solution_and_requested_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert all(
        len([cell for cell in row if cell != sudoku_logic.EMPTY])
        == len(set(cell for cell in row if cell != sudoku_logic.EMPTY))
        for row in puzzle
    )
    assert all(
        len(
            {
                puzzle[row][column]
                for row in range(sudoku_logic.SIZE)
                if puzzle[row][column] != sudoku_logic.EMPTY
            }
        )
        == sum(
            puzzle[row][column] != sudoku_logic.EMPTY
            for row in range(sudoku_logic.SIZE)
        )
        for column in range(sudoku_logic.SIZE)
    )
    assert all(
        len(
            [
                puzzle[row][column]
                for row in range(box_row, box_row + 3)
                for column in range(box_column, box_column + 3)
                if puzzle[row][column] != sudoku_logic.EMPTY
            ]
        )
        == len(
            {
                puzzle[row][column]
                for row in range(box_row, box_row + 3)
                for column in range(box_column, box_column + 3)
                if puzzle[row][column] != sudoku_logic.EMPTY
            }
        )
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert all(set(row) == set(range(1, sudoku_logic.SIZE + 1)) for row in solution)
    assert all(
        {solution[row][column] for row in range(sudoku_logic.SIZE)}
        == set(range(1, sudoku_logic.SIZE + 1))
        for column in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1


@pytest.mark.parametrize('difficulty, expected_clues', [
    ('easy', 45),
    ('medium', 35),
    ('hard', 25),
])
def test_generate_puzzle_supports_difficulty_levels(difficulty, expected_clues):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == expected_clues
    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_rejects_unknown_difficulty():
    with pytest.raises(ValueError, match='difficulty'):
        sudoku_logic.generate_puzzle(difficulty='expert')


def test_count_solutions_identifies_zero_one_and_multiple_solutions():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(solution)) == 1
    assert sudoku_logic.count_solutions(sudoku_logic.create_empty_board()) == 2

    invalid_board = sudoku_logic.deep_copy(solution)
    invalid_board[0][1] = invalid_board[0][0]
    assert sudoku_logic.count_solutions(invalid_board) == 0


def test_generated_puzzles_have_exactly_one_solution():
    for _ in range(5):
        puzzle, _ = sudoku_logic.generate_puzzle(clues=35)

        assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1


def test_deep_copy_does_not_modify_original_board():
    board = sudoku_logic.create_empty_board()
    copied_board = sudoku_logic.deep_copy(board)
    copied_board[0][0] = 1

    assert board[0][0] == sudoku_logic.EMPTY