"""Head-to-head evaluation of strategies against the dealer (notebook cells 60-62)."""

import random
from collections.abc import Mapping
from dataclasses import dataclass

from blackjack.ai.base import Strategy
from blackjack.game.cards import Card, create_deck
from blackjack.game.dealer import play_dealer
from blackjack.game.engine import play_hand
from blackjack.game.hand import calculate_score
from blackjack.game.rules import Outcome, evaluate_outcome


@dataclass
class ComparisonResult:
    name: str
    wins: int = 0
    losses: int = 0
    ties: int = 0

    @property
    def games(self) -> int:
        return self.wins + self.losses + self.ties

    @property
    def win_rate(self) -> float:
        return self.wins / self.games if self.games else 0.0

    def record(self, outcome: Outcome) -> None:
        if outcome is Outcome.WIN:
            self.wins += 1
        elif outcome is Outcome.LOSS:
            self.losses += 1
        else:
            self.ties += 1


def play_solo_game(strategy: Strategy, deck: list[Card]) -> Outcome:
    """One strategy against the dealer on `deck`. The caller's deck is not modified."""
    deck = list(deck)
    hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    score = play_hand(strategy, deck, hand, dealer_hand[0])
    play_dealer(deck, dealer_hand)
    return evaluate_outcome(score, calculate_score(dealer_hand))


def compare_strategies(
    strategies: Mapping[str, Strategy],
    games: int = 1000,
    seed: int | None = None,
) -> dict[str, ComparisonResult]:
    """Play every strategy on the same shuffled decks (a paired comparison).

    Strategies should not learn during evaluation; the Q-learning agent's `decide`
    is greedy and read-only. The same seed gives the same results.
    """
    rng = random.Random(seed)
    results = {name: ComparisonResult(name) for name in strategies}
    for _ in range(games):
        deck = create_deck(rng)
        for name, strategy in strategies.items():
            results[name].record(play_solo_game(strategy, deck))
    return results
