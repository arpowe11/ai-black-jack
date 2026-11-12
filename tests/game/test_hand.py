import pytest

from blackjack.game.hand import calculate_score, has_usable_ace, is_bust


@pytest.mark.parametrize("ranks, score, soft", [
    (("10", "7"), 17, False),
    (("A", "6"), 17, True),
    (("A", "9", "5"), 15, False),   # ace demoted to 1
    (("A", "A"), 12, True),         # one ace 11, one ace 1
    (("A", "K"), 21, True),
    (("K", "Q", "5"), 25, False),
    (("A", "A", "9"), 21, True),
])
def test_score_and_soft(hand, ranks, score, soft):
    cards = hand(*ranks)
    assert calculate_score(cards) == score
    assert has_usable_ace(cards) is soft


@pytest.mark.parametrize("ranks, bust", [
    (("K", "Q"), False),
    (("K", "Q", "2"), True),
    (("A", "K", "5"), False),
])
def test_is_bust(hand, ranks, bust):
    assert is_bust(hand(*ranks)) is bust
