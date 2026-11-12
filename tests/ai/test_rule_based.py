import pytest

from blackjack.ai.base import Action, GameState, get_game_state
from blackjack.ai.rule_based import RuleBasedStrategy


@pytest.mark.parametrize("score, dealer, soft, expected", [
    # cases from notebook cell 33
    (10, 6, False, Action.HIT),
    (15, 6, False, Action.STAND),
    (15, 10, False, Action.HIT),
    (12, 2, False, Action.HIT),
    (18, 10, True, Action.HIT),
    (20, 10, False, Action.STAND),
    # hard-hand boundaries
    (11, 6, False, Action.HIT),
    (12, 4, False, Action.STAND),
    (12, 7, False, Action.HIT),
    (13, 5, False, Action.STAND),
    (16, 7, False, Action.HIT),
    (17, 10, False, Action.STAND),
    # soft-hand boundaries
    (17, 6, True, Action.HIT),
    (18, 8, True, Action.STAND),
    (18, 9, True, Action.HIT),
    (19, 10, True, Action.STAND),
])
def test_rule_based(score, dealer, soft, expected):
    assert RuleBasedStrategy().decide(GameState(score, dealer, soft)) == expected


def test_get_game_state_soft_hand(hand):
    state = get_game_state(hand("A", "7"), hand("10")[0])
    assert state == GameState(score=18, dealer_value=10, usable_ace=True)


def test_get_game_state_ace_counted_as_one(hand):
    state = get_game_state(hand("A", "9", "5"), hand("K")[0])
    assert state == GameState(score=15, dealer_value=10, usable_ace=False)


def test_get_game_state_two_aces(hand):
    state = get_game_state(hand("A", "A"), hand("6")[0])
    assert state == GameState(score=12, dealer_value=6, usable_ace=True)


def test_get_game_state_no_ace(hand):
    state = get_game_state(hand("10", "7"), hand("6")[0])
    assert state == GameState(score=17, dealer_value=6, usable_ace=False)
