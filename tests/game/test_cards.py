import random

import pytest

from blackjack.game.cards import card_value, create_deck


def test_deck_has_52_unique_cards(rng):
    deck = create_deck(rng)
    assert len(deck) == 52
    assert len({(c["rank"], c["suit"]) for c in deck}) == 52


def test_same_seed_gives_same_deck():
    assert create_deck(random.Random(42)) == create_deck(random.Random(42))


def test_different_seeds_give_different_decks():
    assert create_deck(random.Random(1)) != create_deck(random.Random(2))


@pytest.mark.parametrize("rank, expected", [
    ("2", 2), ("9", 9), ("10", 10),
    ("Jack", 10), ("Queen", 10), ("King", 10),
    ("Ace", 11),
])
def test_card_value(rank, expected):
    assert card_value({"rank": rank, "suit": "Hearts"}) == expected
