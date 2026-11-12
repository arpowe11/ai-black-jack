"""Baseline strategy: hit below 17, stand on 17 or more (mirrors the dealer)."""

from blackjack.ai.base import Action, GameState
from blackjack.game.rules import DEALER_STAND


class BaselineStrategy:
    def decide(self, state: GameState) -> Action:
        return Action.HIT if state.score < DEALER_STAND else Action.STAND
