"""Unit tests for the Perfect Guess backend."""

from __future__ import annotations

import random
import unittest

from backend.game_logic import (
    MAX_NUMBER,
    MIN_NUMBER,
    GameFinishedError,
    GuessOutcome,
    InvalidGuessError,
    PerfectGuessGame,
)


class FixedRandom:
    """Deterministic random source that records the requested range."""

    def __init__(self, value: int) -> None:
        self.value = value
        self.bounds: tuple[int, int] | None = None

    def randint(self, a: int, b: int) -> int:
        self.bounds = (a, b)
        return self.value


class GameInitializationTests(unittest.TestCase):
    def test_initialization_with_generated_number(self) -> None:
        rng = FixedRandom(42)

        game = PerfectGuessGame(rng=rng)

        self.assertEqual(game.secret_number, 42)
        self.assertEqual(rng.bounds, (MIN_NUMBER, MAX_NUMBER))
        self.assertEqual(game.attempts, 0)
        self.assertFalse(game.is_won)

    def test_initialization_with_explicit_secret_number(self) -> None:
        game = PerfectGuessGame(secret_number=73)

        self.assertEqual(game.secret_number, 73)
        self.assertEqual(game.attempts, 0)
        self.assertFalse(game.is_won)

    def test_random_generation_stays_within_bounds(self) -> None:
        rng = random.Random(2024)

        for _ in range(500):
            game = PerfectGuessGame(rng=rng)
            self.assertGreaterEqual(game.secret_number, MIN_NUMBER)
            self.assertLessEqual(game.secret_number, MAX_NUMBER)

    def test_random_generation_respects_minimum_boundary(self) -> None:
        game = PerfectGuessGame(rng=FixedRandom(MIN_NUMBER))

        self.assertEqual(game.secret_number, 1)

    def test_random_generation_respects_maximum_boundary(self) -> None:
        game = PerfectGuessGame(rng=FixedRandom(MAX_NUMBER))

        self.assertEqual(game.secret_number, 100)

    def test_custom_range_is_forwarded_to_random_source(self) -> None:
        rng = FixedRandom(5)

        game = PerfectGuessGame(rng=rng, min_number=5, max_number=10)

        self.assertEqual(game.secret_number, 5)
        self.assertEqual(rng.bounds, (5, 10))
        self.assertEqual(game.min_number, 5)
        self.assertEqual(game.max_number, 10)

    def test_invalid_bounds_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PerfectGuessGame(min_number=10, max_number=1)

    def test_invalid_secret_number_is_rejected(self) -> None:
        invalid_values = (0, 101, "50", 50.5, True)

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises((InvalidGuessError, TypeError)):
                    PerfectGuessGame(secret_number=value)  # type: ignore[arg-type]


class GuessEvaluationTests(unittest.TestCase):
    def test_correct_guess(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        result = game.make_guess(50)

        self.assertEqual(result.outcome, GuessOutcome.CORRECT)
        self.assertTrue(result.won)
        self.assertEqual(result.guess, 50)
        self.assertEqual(result.attempts, 1)

    def test_guess_too_high(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        result = game.make_guess(75)

        self.assertEqual(result.outcome, GuessOutcome.TOO_HIGH)
        self.assertFalse(result.won)
        self.assertEqual(result.hint, "Enter a lower number!!!")

    def test_guess_too_low(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        result = game.make_guess(25)

        self.assertEqual(result.outcome, GuessOutcome.TOO_LOW)
        self.assertFalse(result.won)
        self.assertEqual(result.hint, "Enter a higher number!!!")

    def test_minimum_boundary_can_be_guessed(self) -> None:
        game = PerfectGuessGame(secret_number=MIN_NUMBER)

        result = game.make_guess(MIN_NUMBER)

        self.assertEqual(result.outcome, GuessOutcome.CORRECT)
        self.assertTrue(result.won)

    def test_maximum_boundary_can_be_guessed(self) -> None:
        game = PerfectGuessGame(secret_number=MAX_NUMBER)

        result = game.make_guess(MAX_NUMBER)

        self.assertEqual(result.outcome, GuessOutcome.CORRECT)
        self.assertTrue(result.won)

    def test_non_integer_guesses_are_rejected(self) -> None:
        game = PerfectGuessGame(secret_number=50)
        invalid_values = ("50", 50.0, None, True, [50])

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(InvalidGuessError):
                    game.make_guess(value)  # type: ignore[arg-type]

        self.assertEqual(game.attempts, 0)

    def test_out_of_range_guesses_are_rejected(self) -> None:
        game = PerfectGuessGame(secret_number=50)
        invalid_values = (0, 101, -1, 1000)

        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(InvalidGuessError):
                    game.make_guess(value)

        self.assertEqual(game.attempts, 0)
        self.assertFalse(game.is_won)


class GameStateTests(unittest.TestCase):
    def test_attempt_counting(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        self.assertEqual(game.make_guess(25).attempts, 1)
        self.assertEqual(game.make_guess(75).attempts, 2)
        self.assertEqual(game.make_guess(50).attempts, 3)
        self.assertEqual(game.attempts, 3)

    def test_invalid_guesses_do_not_increase_attempts(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        with self.assertRaises(InvalidGuessError):
            game.make_guess(0)
        with self.assertRaises(InvalidGuessError):
            game.make_guess("50")  # type: ignore[arg-type]
        with self.assertRaises(InvalidGuessError):
            game.make_guess(1000)

        self.assertEqual(game.attempts, 0)

    def test_winning_condition(self) -> None:
        game = PerfectGuessGame(secret_number=50)

        self.assertFalse(game.is_won)
        game.make_guess(49)
        self.assertFalse(game.is_won)
        game.make_guess(51)
        self.assertFalse(game.is_won)

        result = game.make_guess(50)

        self.assertTrue(game.is_won)
        self.assertTrue(result.won)
        self.assertEqual(result.outcome, GuessOutcome.CORRECT)

    def test_guessing_after_win_is_rejected(self) -> None:
        game = PerfectGuessGame(secret_number=50)
        game.make_guess(50)

        with self.assertRaises(GameFinishedError):
            game.make_guess(50)

        self.assertEqual(game.attempts, 1)


if __name__ == "__main__":
    unittest.main()
