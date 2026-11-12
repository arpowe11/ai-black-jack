import pytest

from blackjack.ai.base import Action, GameState
from blackjack.ai.baseline import BaselineStrategy


@pytest.mark.parametrize("score, expected", [
    (12, Action.HIT),
    (16, Action.HIT),
    (17, Action.STAND),
    (20, Action.STAND),
])
def test_baseline(score, expected):
    assert BaselineStrategy().decide(GameState(score, 10, False)) == expected


def test_baseline_ignores_dealer_and_soft_hand():
    strategy = BaselineStrategy()
    assert strategy.decide(GameState(16, 2, True)) == Action.HIT
    assert strategy.decide(GameState(18, 10, True)) == Action.STAND
