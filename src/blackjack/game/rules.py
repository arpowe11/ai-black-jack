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


def evaluate_head_to_head(score: int, rival_score: int) -> Outcome:
    """Outcome for one player against another player (no dealer advantage).

    Unlike against the dealer, a bust is not an automatic loss when the rival busts
    too: if both bust it is a tie.
    """
    if score > BLACKJACK and rival_score > BLACKJACK:
        return Outcome.TIE
    return evaluate_outcome(score, rival_score)
