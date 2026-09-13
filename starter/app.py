from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}

def get_valid_board():
    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return None
    if any(
        not isinstance(row, list)
        or len(row) != sudoku_logic.SIZE
        or any(
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= sudoku_logic.SIZE
            for value in row
        )
        for row in board
    ):
        return None
    return board

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    try:
        if difficulty is None:
            clues = int(request.args.get('clues', 35))
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
        else:
            puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    except (ValueError, RuntimeError) as error:
        return jsonify({'error': str(error)}), 400
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle})

@app.route('/hint', methods=['POST'])
def provide_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    board = get_valid_board()
    if board is None:
        return jsonify({'error': 'Invalid board'}), 400

    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] == sudoku_logic.EMPTY and board[row][column] == sudoku_logic.EMPTY:
                board_value = solution[row][column]
                CURRENT['hints_used'] += 1
                return jsonify({
                    'hint': {'row': row, 'column': column, 'value': board_value},
                    'hints_used': CURRENT['hints_used'],
                })

    return jsonify({'hint': None, 'hints_used': CURRENT['hints_used']})

@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    board = get_valid_board()
    if board is None:
        return jsonify({'error': 'Invalid board'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != sudoku_logic.EMPTY and board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)