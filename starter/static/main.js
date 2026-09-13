// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const THEME_KEY = 'sudokuTheme';
let puzzle = [];
let validationRequest = 0;
let timerInterval = null;
let timerStartedAt = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let completedScore = null;
let scoreSubmitted = false;

function formatElapsedTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatElapsedTime(elapsedSeconds);
}

function updateTimer() {
  if (timerStartedAt === null) return;
  elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  updateTimerDisplay();
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  updateTimer();
  timerStartedAt = null;
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  timerStartedAt = Date.now();
  updateTimerDisplay();
  timerInterval = setInterval(updateTimer, 1000);
}

window.sudokuGame = {
  getElapsedSeconds: () => elapsedSeconds
};

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = selectedTheme;
  document.getElementById('theme-toggle').innerText = selectedTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
}

function loadTheme() {
  try {
    return localStorage.getItem(THEME_KEY) === 'dark' ? 'dark' : 'light';
  } catch (error) {
    return 'light';
  }
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    localStorage.setItem(THEME_KEY, nextTheme);
  } catch (error) {
    return;
  }
}

function readLeaderboard() {
  try {
    const stored = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    if (!Array.isArray(stored)) return [];
    return stored.filter(entry => (
      entry && typeof entry.name === 'string' && entry.name.trim() &&
      Number.isFinite(entry.time) && typeof entry.difficulty === 'string'
    ));
  } catch (error) {
    return [];
  }
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  const scores = readLeaderboard().sort((first, second) => first.time - second.time).slice(0, 10);
  body.innerHTML = '';
  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    const storedHints = Number.isInteger(score.hints_used) ? score.hints_used : 0;
    row.innerHTML = `<td>${index + 1}</td><td></td><td>${formatElapsedTime(score.time)}</td><td>${score.difficulty}</td><td>${storedHints}</td>`;
    row.children[1].textContent = score.name;
    body.appendChild(row);
  });
}

function saveScore() {
  if (scoreSubmitted || completedScore === null) return;
  const nameInput = document.getElementById('player-name');
  const name = nameInput.value.trim();
  if (!name) return;

  const scores = readLeaderboard()
    .concat({...completedScore, name})
    .sort((first, second) => first.time - second.time)
    .slice(0, 10);
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch (error) {
    return;
  }
  scoreSubmitted = true;
  nameInput.disabled = true;
  document.getElementById('submit-score').disabled = true;
  renderLeaderboard();
}

function showScoreEntry() {
  if (scoreSubmitted) return;
  document.getElementById('score-entry').hidden = false;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        checkSolution();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  validationRequest += 1;
  puzzle = puz;
  document.getElementById('hint-count').innerText = 'Hints used: 0';
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function getCurrentBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

async function newGame() {
  resetTimer();
  hintsUsed = 0;
  completedScore = null;
  scoreSubmitted = false;
  document.getElementById('score-entry').hidden = true;
  document.getElementById('player-name').value = '';
  document.getElementById('player-name').disabled = false;
  document.getElementById('submit-score').disabled = false;
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  startTimer();
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const requestId = ++validationRequest;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  if (requestId !== validationRequest) return;
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'message-error';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  const isComplete = board.every(row => row.every(value => value !== 0));
  if (incorrect.size === 0 && isComplete) {
    stopTimer();
    if (completedScore === null) {
      completedScore = {
        time: window.sudokuGame.getElapsedSeconds(),
        difficulty: document.getElementById('difficulty').value,
        hints_used: hintsUsed
      };
    }
    showScoreEntry();
    msg.className = 'message-success';
    msg.innerText = `Congratulations! You solved it in ${formatElapsedTime(completedScore.time)} using ${completedScore.hints_used} hints.`;
  } else {
    msg.className = 'message-error';
    msg.innerText = incorrect.size > 0 ? 'Some cells are incorrect.' : '';
  }
}

async function requestHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: getCurrentBoard()})
  });
  const data = await res.json();
  if (data.error) return;

  hintsUsed = Number.isInteger(data.hints_used) ? data.hints_used : hintsUsed;
  document.getElementById('hint-count').innerText = `Hints used: ${data.hints_used}`;
  if (!data.hint) return;

  const {row, column, value} = data.hint;
  const input = document.getElementById('sudoku-board').getElementsByTagName('input')[row * SIZE + column];
  input.value = value;
  input.disabled = true;
  input.className = 'sudoku-cell hint';
  checkSolution();
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(loadTheme());
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('submit-score').addEventListener('click', saveScore);
  renderLeaderboard();
  // initialize
  newGame();
});