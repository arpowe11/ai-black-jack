"""All console I/O: the human player's prompt and the round renderer."""

import random

from blackjack.ai.base import Action, GameState, Strategy
from blackjack.game.cards import Card, card_value
from blackjack.game.engine import Event, RoundResult, play_round
from blackjack.game.hand import calculate_score
from blackjack.game.rules import BLACKJACK

# Order the hands are listed in on the board.
BOARD_ORDER = ("Dealer", "Player", "AI")


def format_card(card: Card) -> str:
    return f"{card['rank']} of {card['suit']}"


def format_row(label: str, cards: list[Card], hide_second: bool = False) -> str:
    """One line of the board: who, their cards, and their score."""
    if hide_second and len(cards) >= 2:
        text = f"{format_card(cards[0])}, [hidden]"
        summary = f"(showing {card_value(cards[0])})"
    else:
        text = ", ".join(format_card(c) for c in cards)
        score = calculate_score(cards)
        summary = f"= {score}" + (" BUST" if score > BLACKJACK else "")
    return f"{label:<7}: {text}  {summary}"


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
    """Turns engine events into text, keeping every hand on screen together.

    A board listing the dealer, the player, and the AI (with scores) is printed after
    the deal, before each of the player's decisions, and when the dealer's turn begins.
    The dealer's second card stays hidden until then.
    """

    def __init__(self) -> None:
        self.hands: dict[str, list[Card]] = {who: [] for who in BOARD_ORDER}
        self.dealer_hidden = False
        self._started = False

    def board(self) -> None:
        print()
        for who in BOARD_ORDER:
            hide = who == "Dealer" and self.dealer_hidden
            print(format_row(who, self.hands[who], hide_second=hide))
        print()

    def __call__(self, event: Event) -> None:
        who = event.who
        if event.kind == "deal" and event.card:
            if not self._started:
                print("--- Initial Deal ---")
                self._started = True
            self.hands[who].append(event.card)
            if not event.visible:
                self.dealer_hidden = True
                self.board()                      # the last card dealt
        elif event.kind == "turn":
            if who == "Dealer":
                self.dealer_hidden = False        # reveal the hole card
            print(f"\n--- {who}'s Turn ---")
            if who == "Dealer":
                self.board()
        elif event.kind == "score":
            if who == "Player":
                self.board()                      # shown before every decision
            elif who == "AI":
                print(f"AI's current score: {event.score}")
        elif event.kind == "hit" and event.card:
            self.hands[who].append(event.card)
            print(f"{who} draws: {format_card(event.card)}")
        elif event.kind == "stand":
            print(f"{who} stands.")
        elif event.kind == "bust":
            print(f"{who} busts with {event.score}!")
        elif event.kind == "empty":
            print("No cards remaining.")


def render_results(result: RoundResult) -> None:
    print("\n--- Final Results ---")
    print(format_row("Dealer", result.dealer_hand))
    print(format_row("Player", result.player_hand))
    print(format_row("AI", result.ai_hand))
    print()
    print("You are up against both the dealer and the AI:")
    print(f"  Player vs Dealer: {result.player_outcome.value}")
    print(f"  Player vs AI:     {result.player_vs_ai.value}")
    print()
    print(f"  AI vs Dealer:     {result.ai_outcome.value}")
    print(f"  AI vs Player:     {result.ai_vs_player.value}")


def play_game(ai: Strategy, rng: random.Random | None = None) -> RoundResult:
    """Play one interactive round: human player and AI player each against the dealer."""
    print("===================================================")
    print("  Welcome to the ultimate Black Jack challenge!")
    print("===================================================")
    result = play_round(HumanStrategy(), ai, rng=rng, emit=ConsoleRenderer())
    render_results(result)
    return result
