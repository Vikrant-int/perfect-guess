"""Core game logic for Perfect Guess.

This module contains no terminal input or output. Any interface (terminal,
desktop, or web) can reuse :class:`PerfectGuessGame` without duplicating the
rules of the game.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

MIN_NUMBER = 1
MAX_NUMBER = 100


class InvalidGuessError(ValueError):
    """Raised when a guess is not an integer within the allowed range."""


class GameFinishedError(RuntimeError):
    """Raised when a guess is made after the game has already been won."""


class RandomSource(Protocol):
    """Protocol for the random source used to generate a secret number."""

    def randint(self, a: int, b: int) -> int:
        """Return a random integer between ``a`` and ``b``, inclusive."""


class GuessOutcome(str, Enum):
    """Possible outcomes of a single guess."""

    TOO_LOW = "too_low"
    TOO_HIGH = "too_high"
    CORRECT = "correct"


@dataclass(frozen=True)
class GuessResult:
    """The result of one valid guess.

    Attributes:
        guess: The value that was guessed.
        outcome: Whether the guess was too low, too high, or correct.
        attempts: The total number of valid guesses made so far.
        won: Whether this guess won the game.
        hint: A user-facing hint derived from ``outcome``.
    """

    guess: int
    outcome: GuessOutcome
    attempts: int
    won: bool

    @property
    def hint(self) -> str:
        """Return a friendly hint for the result."""
        if self.outcome is GuessOutcome.TOO_LOW:
            return "Enter a higher number!!!"
        if self.outcome is GuessOutcome.TOO_HIGH:
            return "Enter a lower number!!!"
        return "You guessed correctly!"


class PerfectGuessGame:
    """A single game of Perfect Guess.

    The class owns the secret number, validates guesses, compares each guess
    with the secret, tracks attempts, and reports whether the game was won.

    Args:
        secret_number: Optional fixed secret number. When omitted, a number is
            generated with ``rng`` (or the standard :mod:`random` module).
        rng: Optional random source exposing ``randint(a, b)``. Injecting a
            deterministic source makes random generation testable.
        min_number: Smallest permitted secret/guess value.
        max_number: Largest permitted secret/guess value.

    Raises:
        ValueError: If the bounds are invalid or ``secret_number`` is outside
            the permitted range.
        TypeError: If ``secret_number`` is not an integer.
    """

    def __init__(
        self,
        secret_number: int | None = None,
        *,
        rng: RandomSource | None = None,
        min_number: int = MIN_NUMBER,
        max_number: int = MAX_NUMBER,
    ) -> None:
        if min_number > max_number:
            raise ValueError("min_number must be less than or equal to max_number")

        self._min_number = min_number
        self._max_number = max_number
        self._random = rng if rng is not None else random
        self._attempts = 0
        self._won = False

        if secret_number is None:
            generated = self._random.randint(min_number, max_number)
            if not isinstance(generated, int) or isinstance(generated, bool):
                raise TypeError("The random source must return an integer")
            secret_number = generated

        self._secret_number = self._validate_number(
            secret_number, "secret_number"
        )

    @property
    def secret_number(self) -> int:
        """The number the player is trying to guess."""
        return self._secret_number

    @property
    def attempts(self) -> int:
        """Number of valid guesses made so far."""
        return self._attempts

    @property
    def is_won(self) -> bool:
        """Whether the player has guessed the secret number."""
        return self._won

    @property
    def min_number(self) -> int:
        """Smallest permitted guess."""
        return self._min_number

    @property
    def max_number(self) -> int:
        """Largest permitted guess."""
        return self._max_number

    def make_guess(self, guess: int) -> GuessResult:
        """Validate and evaluate one guess.

        Invalid guesses do not increase the attempt counter and do not end the
        game. A valid guess always increments the counter.

        Args:
            guess: The integer value to evaluate.

        Returns:
            A :class:`GuessResult` describing the outcome.

        Raises:
            InvalidGuessError: If ``guess`` is not an integer in the permitted
                range.
            GameFinishedError: If the game has already been won.
        """
        if self._won:
            raise GameFinishedError("This game has already been won")

        validated_guess = self._validate_number(guess, "guess")
        self._attempts += 1

        if validated_guess < self._secret_number:
            outcome = GuessOutcome.TOO_LOW
        elif validated_guess > self._secret_number:
            outcome = GuessOutcome.TOO_HIGH
        else:
            outcome = GuessOutcome.CORRECT
            self._won = True

        return GuessResult(
            guess=validated_guess,
            outcome=outcome,
            attempts=self._attempts,
            won=self._won,
        )

    def _validate_number(self, value: int, field_name: str) -> int:
        """Return ``value`` if it is a valid in-range integer."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise InvalidGuessError(f"{field_name} must be an integer")

        if not self._min_number <= value <= self._max_number:
            raise InvalidGuessError(
                f"{field_name} must be between "
                f"{self._min_number} and {self._max_number}"
            )

        return value


__all__ = [
    "MAX_NUMBER",
    "MIN_NUMBER",
    "GameFinishedError",
    "GuessOutcome",
    "GuessResult",
    "InvalidGuessError",
    "PerfectGuessGame",
    "RandomSource",
]
