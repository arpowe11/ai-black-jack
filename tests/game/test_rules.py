import pytest

from blackjack.game.rules import Outcome, evaluate_head_to_head, evaluate_outcome


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


@pytest.mark.parametrize("score, rival, expected", [
    (20, 18, Outcome.WIN),
    (17, 19, Outcome.LOSS),
    (19, 19, Outcome.TIE),
    (22, 18, Outcome.LOSS),   # I bust, rival doesn't
    (18, 23, Outcome.WIN),    # rival busts, I don't
    (24, 22, Outcome.TIE),    # both bust: no dealer advantage between players
])
def test_evaluate_head_to_head(score, rival, expected):
    assert evaluate_head_to_head(score, rival) is expected
