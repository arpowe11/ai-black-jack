from blackjack.ai.base import Action
from blackjack.ai.baseline import BaselineStrategy
from blackjack.game.engine import Event, play_hand, play_round
from blackjack.game.hand import calculate_score
from blackjack.game.rules import Outcome


class Scripted:
    """Strategy that plays back a fixed list of actions, then stands."""

    def __init__(self, *actions: Action):
        self.actions = list(actions)

    def decide(self, state):
        return self.actions.pop(0) if self.actions else Action.STAND


# Deal order is player, AI, dealer, player, AI, dealer; extra cards follow in draw order.


def test_stand_on_twenty_beats_dealer(stacked_deck):
    deck = stacked_deck("K", "10", "10", "Q", "7", "7")  # player 20, AI 17, dealer 17
    result = play_round(Scripted(), BaselineStrategy(), deck)
    assert (result.player_score, result.ai_score, result.dealer_score) == (20, 17, 17)
    assert result.player_outcome is Outcome.WIN
    assert result.ai_outcome is Outcome.TIE


def test_player_hits_and_busts(stacked_deck):
    deck = stacked_deck("10", "10", "10", "6", "9", "8", "K")
    result = play_round(Scripted(Action.HIT), BaselineStrategy(), deck)
    assert result.player_score == 26
    assert result.player_outcome is Outcome.LOSS
    assert result.ai_score == 19 and result.dealer_score == 18
    assert result.ai_outcome is Outcome.WIN


def test_dealer_draws_to_seventeen(stacked_deck):
    deck = stacked_deck("K", "K", "10", "9", "9", "2", "5", "K")  # dealer 12, draws 5
    result = play_round(Scripted(), Scripted(), deck)
    assert result.dealer_score == 17
    assert len(result.dealer_hand) == 3
    assert len(deck) == 1


def test_dealer_skips_turn_when_everyone_busts(stacked_deck):
    deck = stacked_deck("10", "10", "10", "6", "6", "2", "K", "K", "9")
    result = play_round(Scripted(Action.HIT), BaselineStrategy(), deck)
    assert result.player_score > 21 and result.ai_score > 21
    assert len(result.dealer_hand) == 2          # never drew
    assert len(deck) == 1
    assert result.player_outcome is Outcome.LOSS
    assert result.ai_outcome is Outcome.LOSS


def test_ai_plays_even_after_player_busts(stacked_deck):
    deck = stacked_deck("10", "5", "10", "6", "6", "8", "K", "10")
    result = play_round(Scripted(Action.HIT), BaselineStrategy(), deck)
    assert result.player_score == 26
    assert result.ai_score == 21                  # AI hit 11 and drew a 10


def test_play_hand_emits_events(hand, stacked_deck):
    events: list[Event] = []
    cards = hand("10", "6")
    final = play_hand(Scripted(Action.HIT), stacked_deck("K"), cards, hand("5")[0], "Player", events.append)
    assert final == 26
    assert [e.kind for e in events] == ["turn", "score", "hit", "bust"]
    assert events[2].card == {"rank": "King", "suit": "Spades"}


def test_play_hand_stops_when_deck_is_empty(hand):
    cards = hand("2", "3")
    final = play_hand(Scripted(Action.HIT, Action.HIT), [], cards, hand("5")[0])
    assert final == calculate_score(cards) == 5


def test_seeded_rounds_are_reproducible():
    import random

    a = play_round(BaselineStrategy(), BaselineStrategy(), rng=random.Random(7))
    b = play_round(BaselineStrategy(), BaselineStrategy(), rng=random.Random(7))
    assert a.player_hand == b.player_hand
    assert a.dealer_hand == b.dealer_hand


def test_player_is_also_ranked_against_the_ai(stacked_deck):
    # player 20, AI 17 (baseline stands), dealer 17
    deck = stacked_deck("K", "10", "10", "Q", "7", "7")
    result = play_round(Scripted(), BaselineStrategy(), deck)
    assert result.player_vs_ai is Outcome.WIN

    # player 17, AI 20
    deck = stacked_deck("10", "K", "10", "7", "Q", "7")
    result = play_round(Scripted(), BaselineStrategy(), deck)
    assert result.player_vs_ai is Outcome.LOSS


def test_both_busting_is_a_tie_between_players(stacked_deck):
    deck = stacked_deck("10", "10", "10", "6", "6", "2", "K", "K", "9")
    result = play_round(Scripted(Action.HIT), BaselineStrategy(), deck)
    assert result.player_score > 21 and result.ai_score > 21
    assert result.player_vs_ai is Outcome.TIE
