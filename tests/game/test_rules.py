import pytest

from blackjack.game.rules import Outcome, evaluate_outcome


@pytest.mark.parametrize("player, dealer, expected", [
    (22, 18, Outcome.LOSS),   # player busts
    (20, 22, Outcome.WIN),    # dealer busts
    (20, 18, Outcome.WIN),    # player higher
    (17, 20, Outcome.LOSS),   # dealer higher
    (19, 19, Outcome.TIE),
    (23, 24, Outcome.LOSS),   # both bust: player loses
])
def test_evaluate_outcome(player, dealer, expected):
    assert evaluate_outcome(player, dealer) is expected
