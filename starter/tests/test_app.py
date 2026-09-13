import pytest
from pathlib import Path

import app as app_module
import sudoku_logic

MAIN_JS = Path(__file__).parents[1] / 'static' / 'main.js'


@pytest.fixture
def client():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    with app_module.app.test_client() as test_client:
        yield test_client
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None


def test_index_page_is_available(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'id="timer"' in response.data


def test_timer_client_code_supports_lifecycle_and_elapsed_time():
    javascript = MAIN_JS.read_text()

    assert 'function resetTimer()' in javascript
    assert 'function startTimer()' in javascript
    assert 'stopTimer();' in javascript
    assert 'startTimer();' in javascript
    assert 'formatElapsedTime' in javascript
    assert "getElapsedSeconds: () => elapsedSeconds" in javascript


def test_leaderboard_client_code_supports_persistence_and_top_ten_rules():
    javascript = MAIN_JS.read_text()

    assert "const LEADERBOARD_KEY = 'sudokuLeaderboard'" in javascript
    assert 'JSON.parse(localStorage.getItem(LEADERBOARD_KEY)' in javascript
    assert 'localStorage.setItem(LEADERBOARD_KEY' in javascript
    assert 'slice(0, 10)' in javascript
    assert 'first.time - second.time' in javascript
    assert 'getElapsedSeconds()' in javascript
    assert 'hints_used' in javascript
    assert 'using ${completedScore.hints_used} hints' in javascript
    assert 'let hintsUsed = 0' in javascript
    assert 'hintsUsed = Number.isInteger(data.hints_used)' in javascript
    assert 'hints_used: hintsUsed' in javascript
    assert 'localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores))' in javascript
    assert 'Number.isInteger(score.hints_used) ? score.hints_used : 0' in javascript
    assert 'if (scoreSubmitted || completedScore === null) return' in javascript
    assert "difficulty: document.getElementById('difficulty').value" in javascript
    assert 'scoreSubmitted' in javascript
    assert "document.getElementById('submit-score')" in javascript


def test_leaderboard_markup_contains_required_fields(client):
    response = client.get('/')

    assert b'id="player-name"' in response.data
    assert b'id="submit-score"' in response.data
    assert b'id="leaderboard-body"' in response.data
    assert b'Rank' in response.data
    assert b'Name' in response.data
    assert b'Time' in response.data
    assert b'Difficulty' in response.data
    assert b'Hints' in response.data


def test_theme_markup_and_client_code_support_persistence_and_fallback(client):
    response = client.get('/')
    javascript = MAIN_JS.read_text()
    stylesheet = (MAIN_JS.parent / 'styles.css').read_text()

    assert b'id="theme-toggle"' in response.data
    assert "const THEME_KEY = 'sudokuTheme'" in javascript
    assert 'function applyTheme(theme)' in javascript
    assert 'function loadTheme()' in javascript
    assert 'localStorage.setItem(THEME_KEY, nextTheme)' in javascript
    assert "return 'light';" in javascript
    assert 'dataset.theme' in javascript
    assert ':root[data-theme="dark"]' in stylesheet
    for variable in (
        '--page-background', '--board-background', '--cell-background',
        '--button-background', '--message-error', '--hint-background',
        '--incorrect-background', '--prefilled-background', '--cell-border',
        '--message-success'
    ):
        assert variable in stylesheet
    assert 'input,' in stylesheet
    assert 'message-success' in javascript
    assert 'message-error' in javascript


def test_stylesheet_covers_alternating_sudoku_regions_and_preserves_states():
    stylesheet = (MAIN_JS.parent / 'styles.css').read_text()

    assert '--region-background' in stylesheet
    assert '--region-alternate-background' in stylesheet
    assert ':root[data-theme="dark"]' in stylesheet
    assert '.sudoku-row:nth-child(-n + 3)' in stylesheet
    assert '.sudoku-row:nth-child(n + 4):nth-child(-n + 6)' in stylesheet
    assert '.sudoku-row:nth-child(n + 7)' in stylesheet
    assert '.sudoku-cell:nth-child(-n + 3)' in stylesheet
    assert '.sudoku-cell:nth-child(n + 4):nth-child(-n + 6)' in stylesheet
    assert '.sudoku-cell:nth-child(n + 7)' in stylesheet
    assert '.sudoku-cell:nth-child(3)' in stylesheet
    assert '.sudoku-cell:nth-child(6)' in stylesheet
    assert '.sudoku-cell:focus' in stylesheet
    assert '.sudoku-cell.prefilled' in stylesheet
    assert '.sudoku-cell.hint' in stylesheet
    assert '.sudoku-cell.incorrect' in stylesheet
    assert 'background: var(--focus-background) !important' in stylesheet
    assert 'background: var(--prefilled-background) !important' in stylesheet
    assert 'background: var(--hint-background) !important' in stylesheet
    assert 'background: var(--incorrect-background) !important' in stylesheet


def test_stylesheet_supports_responsive_board_controls_and_leaderboard():
    stylesheet = (MAIN_JS.parent / 'styles.css').read_text()

    assert 'overflow-x: hidden' in stylesheet
    assert 'width: min(100%, 450px)' in stylesheet
    assert 'grid-template-columns: repeat(9, minmax(0, 1fr))' in stylesheet
    assert 'aspect-ratio: 1' in stylesheet
    assert 'font-size: clamp(14px, 4vw, 20px)' in stylesheet
    assert 'flex-wrap: wrap' in stylesheet
    assert 'table-layout: fixed' in stylesheet
    assert 'overflow-wrap: anywhere' in stylesheet
    assert '@media (max-width: 520px)' in stylesheet


def test_check_client_only_highlights_missing_cells_on_explicit_check():
    javascript = MAIN_JS.read_text()

    assert 'async function checkSolution(highlightMissing = false)' in javascript
    assert 'if (highlightMissing && board[Math.floor(idx / SIZE)][idx % SIZE] === 0)' in javascript
    assert "addEventListener('input', (e) =>" in javascript
    assert "addEventListener('click', () => checkSolution(true))" in javascript


def test_new_game_returns_puzzle_and_stores_solution(client):
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
    assert app_module.CURRENT['solution'] is not None
    assert app_module.CURRENT['hints_used'] == 0


@pytest.mark.parametrize('difficulty, expected_clues', [
    ('easy', 45),
    ('medium', 35),
    ('hard', 25),
])
def test_new_game_accepts_difficulty(client, difficulty, expected_clues):
    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == expected_clues
    assert sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle)) == 1


def test_new_game_rejects_unknown_difficulty(client):
    response = client.get('/new?difficulty=expert')

    assert response.status_code == 400
    assert 'difficulty' in response.get_json()['error']


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_hint_fills_one_empty_cell_with_solution_value(client, difficulty):
    response = client.get(f'/new?difficulty={difficulty}')
    puzzle = response.get_json()['puzzle']
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(puzzle)
    empty_before = sum(cell == sudoku_logic.EMPTY for row in board for cell in row)

    hint_response = client.post('/hint', json={'board': board})
    hint = hint_response.get_json()['hint']
    row, column = hint['row'], hint['column']

    assert hint_response.status_code == 200
    board[row][column] = hint['value']
    assert empty_before - 1 == sum(
        cell == sudoku_logic.EMPTY for row in board for cell in row
    )
    assert puzzle[row][column] == sudoku_logic.EMPTY
    assert hint['value'] == solution[row][column]
    assert app_module.CURRENT['hints_used'] == 1


def test_hints_do_not_overwrite_existing_entries_or_repeat_cells(client):
    client.get('/new?clues=35')
    puzzle = app_module.CURRENT['puzzle']
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(puzzle)
    player_cell = next(
        (row, column)
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
        if board[row][column] == sudoku_logic.EMPTY
    )
    board[player_cell[0]][player_cell[1]] = solution[player_cell[0]][player_cell[1]]

    first = client.post('/hint', json={'board': board}).get_json()
    first_cell = (first['hint']['row'], first['hint']['column'])
    board[first_cell[0]][first_cell[1]] = first['hint']['value']
    second = client.post('/hint', json={'board': board}).get_json()
    second_cell = (second['hint']['row'], second['hint']['column'])

    assert first_cell != player_cell
    assert second_cell != player_cell
    assert second_cell != first_cell
    assert second['hints_used'] == 2


def test_hint_is_noop_when_no_empty_cells_remain(client):
    client.get('/new?clues=35')
    solution = app_module.CURRENT['solution']

    response = client.post('/hint', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'hint': None, 'hints_used': 0}


def test_new_game_resets_hint_count(client):
    client.get('/new?clues=35')
    puzzle = app_module.CURRENT['puzzle']
    client.post('/hint', json={'board': sudoku_logic.deep_copy(puzzle)})

    client.get('/new?difficulty=easy')

    assert app_module.CURRENT['hints_used'] == 0


def test_hint_requires_game_in_progress(client):
    response = client.post('/hint', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize('payload', [
    None,
    {},
    {'board': 'not a board'},
    {'board': [[0] * sudoku_logic.SIZE]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)] + [[0] * (sudoku_logic.SIZE - 1)]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)] + [[0] * 8 + [10]]},
])
def test_hint_rejects_malformed_board_payloads(client, payload):
    client.get('/new')

    response = client.post('/hint', json=payload)

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid board'}


def test_check_solution_requires_game_in_progress(client):
    response = client.post('/check', json={'board': []})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


@pytest.mark.parametrize('payload', [
    None,
    {},
    {'board': 'not a board'},
    {'board': [[0] * sudoku_logic.SIZE]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)] + [[0] * (sudoku_logic.SIZE - 1)]},
    {'board': [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE - 1)] + [[0] * 8 + [10]]},
])
def test_check_solution_rejects_malformed_board_payloads(client, payload):
    client.get('/new')

    response = client.post('/check', json=payload)

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Invalid board'}


def test_check_solution_returns_incorrect_cells(client):
    client.get('/new')
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = (board[0][0] % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': [[0, 0]]}


def test_check_solution_ignores_empty_cells(client):
    response = client.get('/new?clues=35')
    puzzle = response.get_json()['puzzle']

    check_response = client.post('/check', json={'board': puzzle})

    assert check_response.status_code == 200
    assert check_response.get_json() == {'incorrect': []}


def test_check_solution_detects_changed_prefilled_cell(client):
    response = client.get('/new?clues=35')
    puzzle = response.get_json()['puzzle']
    solution = app_module.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    row, column = next(
        (row, column)
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
        if puzzle[row][column] != sudoku_logic.EMPTY
    )
    board[row][column] = (board[row][column] % sudoku_logic.SIZE) + 1

    check_response = client.post('/check', json={'board': board})

    assert check_response.status_code == 200
    assert check_response.get_json() == {'incorrect': [[row, column]]}


def test_check_solution_accepts_current_solution(client):
    client.get('/new')

    response = client.post('/check', json={'board': app_module.CURRENT['solution']})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}