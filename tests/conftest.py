import random

import pytest

SUIT = "Spades"


def make_card(rank: str, suit: str = SUIT) -> dict[str, str]:
    return {"rank": rank, "suit": suit}


@pytest.fixture
def hand():
    """hand("A", "7") -> list of cards. Accepts A/J/Q/K shorthand or full rank names."""
    short = {"A": "Ace", "J": "Jack", "Q": "Queen", "K": "King"}

    def build(*ranks: str):
        return [make_card(short.get(r, r)) for r in ranks]

    return build


@pytest.fixture
def stacked_deck(hand):
    """stacked_deck("5", "K") -> deck that deals cards in the order given (pop() takes the first)."""

    def build(*ranks: str):
        return list(reversed(hand(*ranks)))

    return build


@pytest.fixture
def rng():
    return random.Random(0)
