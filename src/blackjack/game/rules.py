"""Game constants and outcome evaluation."""

from enum import Enum

BLACKJACK = 21
DEALER_STAND = 17


class Outcome(Enum):
    WIN = "Win"
    LOSS = "Loss"
    TIE = "Tie"


def evaluate_outcome(player_score: int, dealer_score: int) -> Outcome:
    """Outcome for the player against the dealer."""
    if player_score > BLACKJACK:
        return Outcome.LOSS
    if dealer_score > BLACKJACK:
        return Outcome.WIN
    if player_score > dealer_score:
        return Outcome.WIN
    if player_score < dealer_score:
        return Outcome.LOSS
    return Outcome.TIE
