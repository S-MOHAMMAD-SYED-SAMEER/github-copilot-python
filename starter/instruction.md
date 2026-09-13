# Sudoku Project Instructions

These instructions guide GitHub Copilot while developing this educational Flask Sudoku project.

## Project Principles

- Preserve existing behavior unless a requirement explicitly changes it.
- Keep the implementation simple and appropriate for a small educational Flask project.
- Prefer the Python standard library, Flask, and existing project dependencies. Do not introduce frameworks, services, or dependencies without a clear need.
- Inspect existing code, tests, and behavior before proposing or accepting changes.
- Evaluate generated code critically and verify it with tests and manual reasoning before accepting it.

## Python and Flask

- Write modern, readable, maintainable Python.
- Follow Flask best practices for routes, request handling, responses, templates, and application configuration.
- Keep application concerns, Sudoku/game logic, and presentation concerns logically separate.
- Use small, focused, reusable functions and components.
- Use clear, descriptive naming conventions. Avoid one-letter names except for conventional, tightly scoped loop variables.
- Add type hints where they improve clarity, especially for public functions, data structures, and route-related boundaries.
- Use consistent error handling with appropriate HTTP status codes and useful client-facing error responses.
- Keep comments and documentation minimal but useful. Explain decisions or non-obvious behavior rather than restating code.
- Keep state management explicit and avoid hidden global coupling where practical.
- Preserve public interfaces and existing behavior unless the requirement calls for a deliberate change.

## Frontend

- Keep HTML, CSS, and JavaScript organized, readable, and maintainable.
- Separate structure, presentation, and behavior instead of embedding large amounts of CSS or JavaScript in templates.
- Build a responsive interface that works on desktop and mobile screens.
- Use semantic HTML, keyboard-friendly controls, visible focus states, sufficient color contrast, and accessible labels where practical.
- Support both light and dark modes without sacrificing readability or usability.
- Clearly distinguish locked/pre-filled cells from player-entered cells using more than color alone where practical.
- Avoid unnecessary visual complexity and keep the interface appropriate for the educational project.

## Required Features

The implementation must support:

- Easy, Medium, and Hard difficulty levels.
- Reliable Sudoku generation with exactly one valid solution.
- Unique-solution validation for generated puzzles and relevant user actions.
- Locked/pre-filled cells that players cannot edit.
- Clear feedback for invalid moves.
- A completion message when the puzzle is correctly solved.
- A Hint action that provides a useful valid move without exposing the entire solution unnecessarily.
- A Check action that identifies incorrect entries without corrupting the game state.
- A visible timer for the active game.
- A Top 10 leaderboard persisted with `localStorage`.
- User-selectable dark and light modes.
- Responsive behavior across desktop and mobile layouts.
- Alternating styling for the 3x3 Sudoku squares to improve board readability.

## Testing and Verification

- Keep code testable by isolating logic from Flask request handling and browser presentation where practical.
- Add or update focused tests for every behavior change.
- Run the full test suite after changes from the project root:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest
  ```

- Do not remove existing tests, skip meaningful coverage, or weaken assertions just to make tests pass.
- When changing frontend behavior, verify the relevant interaction and responsive states in addition to running automated tests.
- Treat failures as evidence to investigate. Do not change expected behavior merely to hide a regression.

## Copilot Workflow

Before editing:

1. Inspect the relevant application code, templates, static assets, tests, and current behavior.
2. Identify the smallest change that satisfies the requirement.
3. State assumptions when behavior is ambiguous.

After editing:

1. Review the generated code for correctness, simplicity, security, accessibility, and consistency with this guide.
2. Run focused tests first when available, then run the full test suite.
3. Check that unrelated behavior and files were not changed.
4. Report any remaining limitations or unverified behavior clearly.

Do not refactor unrelated code, redesign working features without a requirement, or add abstraction for its own sake.
