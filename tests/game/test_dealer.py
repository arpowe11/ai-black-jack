import pytest

from blackjack.game.dealer import dealer_should_hit, play_dealer
from blackjack.game.hand import calculate_score


@pytest.mark.parametrize("ranks, expected", [
    (("10", "6"), True),
    (("10", "7"), False),
    (("A", "6"), False),   # soft 17 stands
    (("K", "Q"), False),
])
def test_dealer_should_hit(hand, ranks, expected):
    assert dealer_should_hit(hand(*ranks)) is expected


def test_dealer_draws_until_17(hand, stacked_deck):
    dealer = hand("7", "5")                 # 12
    deck = stacked_deck("5", "9")           # draws 5 -> 17, stops
    drawn = play_dealer(deck, dealer)
    assert calculate_score(dealer) == 17
    assert len(drawn) == 1
    assert len(deck) == 1


def test_dealer_can_bust(hand, stacked_deck):
    dealer = hand("10", "6")
    play_dealer(stacked_deck("K"), dealer)
    assert calculate_score(dealer) == 26


def test_dealer_stops_on_empty_deck(hand):
    dealer = hand("2", "3")
    assert play_dealer([], dealer) == []
    assert calculate_score(dealer) == 5
