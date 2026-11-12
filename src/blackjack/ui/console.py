"""All console I/O: the human player's prompt and the round renderer."""

import random

from blackjack.ai.base import Action, GameState, Strategy
from blackjack.game.cards import Card
from blackjack.game.engine import Event, RoundResult, play_round


def format_card(card: Card) -> str:
    return f"{card['rank']} of {card['suit']}"


class HumanStrategy:
    """Asks the person at the keyboard whether to hit or stand."""

    def decide(self, state: GameState) -> Action:
        while True:
            choice = input("Would you like to Hit or Stand? ").strip().lower()
            if choice == "hit":
                return Action.HIT
            if choice == "stand":
                return Action.STAND
            print("Please enter Hit or Stand.")


class ConsoleRenderer:
    """Turns engine events into the text the notebook used to print."""

    def __init__(self) -> None:
        self._dealt = False

    def __call__(self, event: Event) -> None:
        who = event.who
        if event.kind == "deal":
            if not self._dealt:
                print("--- Initial Deal ---")
                self._dealt = True
            if event.visible and event.card:
                print(f"{who}'s card: {format_card(event.card)}")
        elif event.kind == "turn":
            print(f"\n--- {who}'s Turn ---")
        elif event.kind == "score":
            print(f"{who}'s current score: {event.score}")
        elif event.kind == "hit" and event.card:
            print(f"{who} draws: {format_card(event.card)}")
        elif event.kind == "stand":
            print(f"{who} stands.")
        elif event.kind == "bust":
            print(f"{who} busts with {event.score}!")
        elif event.kind == "empty":
            print("No cards remaining.")


def render_results(result: RoundResult) -> None:
    print("\n--- Final Results ---")
    print(f"Dealer's cards: {', '.join(format_card(c) for c in result.dealer_hand)}")
    print(f"Player's final score: {result.player_score}")
    print(f"AI's final score: {result.ai_score}")
    print(f"Dealer's final score: {result.dealer_score}")
    print(f"Player vs Dealer: {result.player_outcome.value}")
    print(f"AI vs Dealer: {result.ai_outcome.value}")


def play_game(ai: Strategy, rng: random.Random | None = None) -> RoundResult:
    """Play one interactive round: human player and AI player against the dealer."""
    print("===================================================")
    print("  Welcome to the ultimate Black Jack challenge!")
    print("===================================================")
    result = play_round(HumanStrategy(), ai, rng=rng, emit=ConsoleRenderer())
    render_results(result)
    return result
