"""Command-line entry point: `play`, `train`, and `compare`."""

import argparse
import random
from collections.abc import Sequence
from pathlib import Path

from blackjack.ai.base import Strategy
from blackjack.ai.baseline import BaselineStrategy
from blackjack.ai.evaluation import compare_strategies
from blackjack.ai.q_learning import QLearningAgent
from blackjack.ai.rule_based import RuleBasedStrategy
from blackjack.ai.training import train
from blackjack.ui.console import play_game

DEFAULT_MODEL = Path("models/q_table.json")
AI_CHOICES = ["rule-based", "baseline", "q-learning"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blackjack", description="Blackjack with AI players.")
    sub = parser.add_subparsers(dest="command", required=True)

    play = sub.add_parser("play", help="play a round against the dealer alongside an AI")
    play.add_argument("--ai", choices=AI_CHOICES, default="rule-based",
                      help="strategy for the AI player (default: rule-based)")
    play.add_argument("--model", type=Path, default=DEFAULT_MODEL,
                      help=f"Q-table for --ai q-learning (default: {DEFAULT_MODEL})")
    play.add_argument("--seed", type=int, default=None, help="seed the deck shuffle")

    trn = sub.add_parser("train", help="train the Q-learning agent and save its Q-table")
    trn.add_argument("--games", type=int, default=50_000, help="training games (default: 50000)")
    trn.add_argument("--seed", type=int, default=None, help="seed for reproducible training")
    trn.add_argument("--output", type=Path, default=DEFAULT_MODEL,
                     help=f"where to save the Q-table (default: {DEFAULT_MODEL})")

    cmp = sub.add_parser("compare", help="compare AI strategies on identical decks")
    cmp.add_argument("--games", type=int, default=1000, help="games per strategy (default: 1000)")
    cmp.add_argument("--seed", type=int, default=42, help="seed for the decks (default: 42)")
    cmp.add_argument("--model", type=Path, default=DEFAULT_MODEL,
                     help=f"Q-table to evaluate (default: {DEFAULT_MODEL})")
    return parser


def make_ai(name: str, model: Path) -> Strategy:
    if name == "baseline":
        return BaselineStrategy()
    if name == "q-learning":
        if not model.exists():
            raise SystemExit(f"No trained model at {model}. Run `blackjack train` first.")
        return QLearningAgent.load(model)
    return RuleBasedStrategy()


def cli(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.command == "play":
        ai = make_ai(args.ai, args.model)
        rng = random.Random(args.seed) if args.seed is not None else None
        play_game(ai, rng)

    elif args.command == "train":
        result = train(args.games, seed=args.seed)
        result.agent.save(args.output)
        print(f"Trained {result.games} games "
              f"(wins {result.wins}, losses {result.losses}, ties {result.ties}; "
              f"win rate {result.win_rate:.1%} while exploring)")
        print(f"Learned {len(result.agent.q_table)} states -> {args.output}")

    elif args.command == "compare":
        strategies = {name: make_ai(name, args.model) for name in AI_CHOICES}
        results = compare_strategies(strategies, args.games, args.seed)
        print(f"{args.games} games per strategy, seed {args.seed}, model {args.model}")
        print(f"{'Strategy':<12}{'Wins':>7}{'Losses':>8}{'Ties':>7}{'Win rate':>10}")
        for name, r in results.items():
            print(f"{name:<12}{r.wins:>7}{r.losses:>8}{r.ties:>7}{r.win_rate:>10.1%}")
