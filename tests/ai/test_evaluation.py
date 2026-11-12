from blackjack.ai.base import Action
from blackjack.ai.baseline import BaselineStrategy
from blackjack.ai.evaluation import compare_strategies, play_solo_game
from blackjack.ai.rule_based import RuleBasedStrategy
from blackjack.game.rules import Outcome


class Always:
    def __init__(self, action: Action):
        self.action = action

    def decide(self, state):
        return self.action


# Deck order: AI, AI, dealer, dealer, then draws.


def test_stand_on_twenty_beats_seventeen(stacked_deck):
    deck = stacked_deck("K", "Q", "10", "7")
    assert play_solo_game(Always(Action.STAND), deck) is Outcome.WIN


def test_hitting_sixteen_into_a_king_busts(stacked_deck):
    deck = stacked_deck("10", "6", "10", "7", "K")
    assert play_solo_game(Always(Action.HIT), deck) is Outcome.LOSS


def test_solo_game_does_not_consume_callers_deck(stacked_deck):
    deck = stacked_deck("K", "Q", "10", "7")
    play_solo_game(Always(Action.STAND), deck)
    assert len(deck) == 4


def test_counts_add_up():
    results = compare_strategies({"rule": RuleBasedStrategy(), "base": BaselineStrategy()}, 200, seed=1)
    for r in results.values():
        assert r.games == 200
        assert r.wins + r.losses + r.ties == 200


def test_same_seed_same_results():
    strategies = {"rule": RuleBasedStrategy(), "base": BaselineStrategy()}
    a = compare_strategies(strategies, 300, seed=42)
    b = compare_strategies(strategies, 300, seed=42)
    assert a == b


def test_identical_strategies_get_identical_results():
    results = compare_strategies({"a": RuleBasedStrategy(), "b": RuleBasedStrategy()}, 300, seed=7)
    assert (results["a"].wins, results["a"].losses) == (results["b"].wins, results["b"].losses)


def test_win_rate_of_empty_run_is_zero():
    assert compare_strategies({"x": BaselineStrategy()}, 0)["x"].win_rate == 0.0
