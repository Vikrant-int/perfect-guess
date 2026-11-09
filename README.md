# Perfect Guess

Perfect Guess is a classic number-guessing game written in Python. The
computer chooses a secret number between **1** and **100**, and the player
tries to find it using higher-or-lower hints while the game counts every
attempt.

The project is split into a reusable, UI-independent backend and a thin
terminal interface. The original game rules are preserved, and the backend is
ready to be connected to a future desktop interface without rewriting the game
logic.

## Features

- Random secret number between 1 and 100.
- Higher/lower hints after every guess.
- Accurate attempt counting.
- Clear winning message showing the secret number and attempt count.
- Graceful handling of invalid and out-of-range input.
- Deterministic, injectable random source for testing.
- Backend with no `input()` or `print()` calls.
- Terminal interface that only handles input, output, and presentation.
- Comprehensive test suite using Python's built-in `unittest`.
- No third-party runtime dependencies.

## Technologies Used

- **Python 3.10+**
- **unittest** (Python standard library)
- **random** and **dataclasses** (Python standard library)

## Project Structure

```text
perfect-guess/
|
├── backend/
│   ├── __init__.py
│   └── game_logic.py
├── frontend/
│   └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_game_logic.py
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

- `backend/game_logic.py` contains the complete game rules and state.
- `main.py` is the terminal application and contains no game rules.
- `frontend/` is a placeholder for future UI work.
- `tests/` contains deterministic unit tests for the backend.

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/Vikrant-int/perfect-guess.git
cd perfect-guess
```

The game uses only the Python standard library, so no packages need to be
installed. A virtual environment is still recommended for local development.

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

`requirements.txt` intentionally contains no third-party dependencies.

## How to Run the Game

From the project root:

```bash
python main.py
```

The game will explain the rules, prompt for guesses, and finish when the
secret number is found.

## How to Run Tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

The suite covers correct guesses, too-high and too-low guesses, both
boundaries, invalid values, out-of-range values, attempt counting, the winning
condition, random number boundaries, and game initialization.

## Example Gameplay

```text
================================================
                 PERFECT GUESS
================================================
I'm thinking of a number between 1 and 100.
After each guess I'll tell you to go higher or lower.
Try to find it in as few attempts as possible!

Enter the number: 50
Enter a higher number!!!
Enter the number: 75
Enter a lower number!!!
Enter the number: 62
Enter a higher number!!!
Enter the number: 68
Enter a lower number!!!
Enter the number: 65

You correctly guessed 65 in 5 attempts.
```

Invalid input is handled without ending the game or counting an attempt:

```text
Enter the number: hello
Invalid input. Please enter a whole number.
Enter the number: 101
Invalid guess: guess must be between 1 and 100. Please try again.
```

## Backend Architecture

`PerfectGuessGame` owns the secret number, attempt count, and winning state.
It validates each guess and returns a `GuessResult` containing:

- the guess;
- whether it was too low, too high, or correct;
- the current attempt count;
- whether the game has been won;
- a user-facing hint.

Random generation can be controlled in two ways:

```python
from backend.game_logic import PerfectGuessGame

# Fixed secret number
game = PerfectGuessGame(secret_number=42)

# Or an injected deterministic random source
class FixedRandom:
    def randint(self, a: int, b: int) -> int:
        return 42

game = PerfectGuessGame(rng=FixedRandom())
```

The core module does not import any terminal or UI code, which keeps the
backend reusable.

## Future Desktop UI Development

The `frontend/` package is intentionally empty. A future desktop interface can
be added there and can reuse `PerfectGuessGame` directly:

```python
from backend.game_logic import PerfectGuessGame

game = PerfectGuessGame()
result = game.make_guess(50)

if not result.won:
    show_hint(result.hint)
    show_attempt_count(result.attempts)
```

Planned direction:

- Build a desktop window with an input field, hint area, and attempt counter.
- Start a new game without restarting the application.
- Keep all game rules in `backend/game_logic.py`.
- Add interface-specific tests while leaving the backend test suite unchanged.
- Preserve the terminal application as an alternative way to play.
