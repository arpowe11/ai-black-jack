"""Shared AI types: Action, GameState, and the Strategy protocol."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from blackjack.game.cards import Card, card_value
from blackjack.game.hand import calculate_score, has_usable_ace


class Action(Enum):
    HIT = "hit"
    STAND = "stand"


@dataclass(frozen=True)
class GameState:
    """What a player can see when deciding: own score, dealer's up-card value, soft hand?"""

    score: int
    dealer_value: int
    usable_ace: bool


class Strategy(Protocol):
    def decide(self, state: GameState) -> Action: ...


def get_game_state(hand: list[Card], dealer_card: Card) -> GameState:
    return GameState(
        score=calculate_score(hand),
        dealer_value=card_value(dealer_card),
        usable_ace=has_usable_ace(hand),
    )
