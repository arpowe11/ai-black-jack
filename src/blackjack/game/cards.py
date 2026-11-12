"""Cards and decks. Cards are plain dicts for now: {'rank': 'Ace', 'suit': 'Hearts'}."""

import random

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]
FACE_RANKS = ("Jack", "Queen", "King")

Card = dict[str, str]


def create_deck(rng: random.Random | None = None) -> list[Card]:
    """Return a shuffled 52-card deck. Pass a seeded `rng` for reproducibility."""
    rng = rng or random.Random()
    deck = [{"rank": rank, "suit": suit} for suit in SUITS for rank in RANKS]
    rng.shuffle(deck)
    return deck


def card_value(card: Card) -> int:
    """Face cards are 10, aces are 11 (hand scoring demotes them), others are numeric."""
    rank = card["rank"]
    if rank in FACE_RANKS:
        return 10
    if rank == "Ace":
        return 11
    return int(rank)
