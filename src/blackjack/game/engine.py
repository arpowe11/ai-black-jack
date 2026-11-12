"""Round engine: deals and plays a round. Pure logic; no print() or input().

Anything a UI might want to show is reported through an optional `emit(event)` callback.
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from blackjack.ai.base import Action, Strategy, get_game_state
from blackjack.game.cards import Card, create_deck
from blackjack.game.dealer import play_dealer
from blackjack.game.hand import calculate_score
from blackjack.game.rules import BLACKJACK, Outcome, evaluate_outcome


@dataclass(frozen=True)
class Event:
    """Something that happened in a round.

    kind: "deal", "turn", "score", "hit", "stand", "bust", or "empty" (deck ran out).
    visible: False for a dealt card that starts face down (the dealer's hole card).
    """

    kind: str
    who: str
    card: Card | None = None
    score: int | None = None
    visible: bool = True


Emit = Callable[[Event], None]


def _ignore(event: Event) -> None:
    pass


@dataclass
class RoundResult:
    player_hand: list[Card]
    ai_hand: list[Card]
    dealer_hand: list[Card]
    player_outcome: Outcome
    ai_outcome: Outcome
    deck: list[Card] = field(repr=False, default_factory=list)

    @property
    def player_score(self) -> int:
        return calculate_score(self.player_hand)

    @property
    def ai_score(self) -> int:
        return calculate_score(self.ai_hand)

    @property
    def dealer_score(self) -> int:
        return calculate_score(self.dealer_hand)


def play_hand(
    strategy: Strategy,
    deck: list[Card],
    hand: list[Card],
    dealer_card: Card,
    who: str = "Player",
    emit: Emit = _ignore,
) -> int:
    """Let `strategy` hit or stand until it stands, busts, or the deck runs out.

    Works for any Strategy (human, rule-based, baseline, Q-learning). Mutates
    `deck` and `hand`; returns the final score.
    """
    emit(Event("turn", who))
    while True:
        score = calculate_score(hand)
        if score > BLACKJACK:
            emit(Event("bust", who, score=score))
            break
        emit(Event("score", who, score=score))

        action = strategy.decide(get_game_state(hand, dealer_card))
        if action is Action.STAND:
            emit(Event("stand", who, score=score))
            break
        if not deck:
            emit(Event("empty", who))
            break
        card = deck.pop()
        hand.append(card)
        emit(Event("hit", who, card=card))
    return calculate_score(hand)


def play_round(
    player: Strategy,
    ai: Strategy,
    deck: list[Card] | None = None,
    rng: random.Random | None = None,
    emit: Emit = _ignore,
) -> RoundResult:
    """Deal and play one round: player, then AI, then dealer."""
    if deck is None:
        deck = create_deck(rng)

    hands: dict[str, list[Card]] = {"Player": [], "AI": [], "Dealer": []}
    for i in range(2):
        for who, hand in hands.items():
            card = deck.pop()
            hand.append(card)
            # Only the dealer's second card (the hole card) starts face down.
            emit(Event("deal", who, card=card, visible=(who != "Dealer" or i == 0)))

    player_hand, ai_hand, dealer_hand = hands["Player"], hands["AI"], hands["Dealer"]
    dealer_card = dealer_hand[0]

    player_score = play_hand(player, deck, player_hand, dealer_card, "Player", emit)
    ai_score = play_hand(ai, deck, ai_hand, dealer_card, "AI", emit)

    # The dealer only plays if at least one player is still in.
    if player_score <= BLACKJACK or ai_score <= BLACKJACK:
        emit(Event("turn", "Dealer"))
        emit(Event("score", "Dealer", score=calculate_score(dealer_hand)))
        for card in play_dealer(deck, dealer_hand):
            emit(Event("hit", "Dealer", card=card))
        final = calculate_score(dealer_hand)
        emit(Event("bust" if final > BLACKJACK else "stand", "Dealer", score=final))

    dealer_score = calculate_score(dealer_hand)
    return RoundResult(
        player_hand=player_hand,
        ai_hand=ai_hand,
        dealer_hand=dealer_hand,
        player_outcome=evaluate_outcome(player_score, dealer_score),
        ai_outcome=evaluate_outcome(ai_score, dealer_score),
        deck=deck,
    )
