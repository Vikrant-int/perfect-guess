"""Terminal interface for Perfect Guess.

All game rules live in :mod:`backend.game_logic`; this module is responsible
only for reading input and printing messages.
"""

from __future__ import annotations

from typing import Callable

from backend.game_logic import (
    MAX_NUMBER,
    MIN_NUMBER,
    GuessOutcome,
    InvalidGuessError,
    PerfectGuessGame,
)

InputFunction = Callable[[str], str]
OutputFunction = Callable[[str], None]


def play_game(
    game: PerfectGuessGame | None = None,
    *,
    input_func: InputFunction = input,
    output_func: OutputFunction = print,
) -> int:
    """Play one full game in the terminal and return the number of attempts.

    ``input_func`` and ``output_func`` are injectable so the interface can be
    exercised without real terminal interaction.
    """
    game = game if game is not None else PerfectGuessGame()

    output_func("=" * 48)
    output_func("                 PERFECT GUESS")
    output_func("=" * 48)
    output_func(
        f"I'm thinking of a number between {MIN_NUMBER} and {MAX_NUMBER}."
    )
    output_func("After each guess I'll tell you to go higher or lower.")
    output_func("Try to find it in as few attempts as possible!")
    output_func("")

    while not game.is_won:
        raw_guess = input_func("Enter the number: ")

        try:
            guess = int(raw_guess)
        except ValueError:
            output_func("Invalid input. Please enter a whole number.")
            continue

        try:
            result = game.make_guess(guess)
        except InvalidGuessError as exc:
            output_func(f"Invalid guess: {exc}. Please try again.")
            continue

        if result.outcome is GuessOutcome.CORRECT:
            attempt_word = "attempt" if result.attempts == 1 else "attempts"
            output_func(
                f"\nYou correctly guessed {result.guess} "
                f"in {result.attempts} {attempt_word}."
            )
            return result.attempts

        output_func(result.hint)

    return game.attempts


def main() -> None:
    """Run the terminal application."""
    try:
        play_game()
    except (EOFError, KeyboardInterrupt):
        print("\nGame cancelled. Thanks for playing!")


if __name__ == "__main__":
    main()
