"""Hand scoring."""

from blackjack.game.cards import Card, card_value
from blackjack.game.rules import BLACKJACK


def calculate_score(hand: list[Card]) -> int:
    """Best score for the hand: aces count 11 unless that would bust, then 1."""
    score = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card["rank"] == "Ace")
    while score > BLACKJACK and aces > 0:
        score -= 10
        aces -= 1
    return score


def has_usable_ace(hand: list[Card]) -> bool:
    """True if an ace is currently counted as 11 (a 'soft' hand)."""
    low_total = sum(1 if card["rank"] == "Ace" else card_value(card) for card in hand)
    has_ace = any(card["rank"] == "Ace" for card in hand)
    return has_ace and low_total + 10 <= BLACKJACK


def is_bust(hand: list[Card]) -> bool:
    return calculate_score(hand) > BLACKJACK
