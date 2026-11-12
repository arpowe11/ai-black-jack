"""The dealer: one silent implementation. Rendering belongs to the UI layer."""

from blackjack.game.cards import Card
from blackjack.game.hand import calculate_score
from blackjack.game.rules import DEALER_STAND


def dealer_should_hit(hand: list[Card]) -> bool:
    return calculate_score(hand) < DEALER_STAND


def play_dealer(deck: list[Card], hand: list[Card]) -> list[Card]:
    """Draw into `hand` until the dealer reaches 17 or the deck runs out.

    Mutates `deck` and `hand`. Returns the cards drawn, so a UI can display them.
    """
    drawn: list[Card] = []
    while dealer_should_hit(hand) and deck:
        card = deck.pop()
        hand.append(card)
        drawn.append(card)
    return drawn
