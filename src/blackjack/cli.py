"""Command-line entry point. `train` and `compare` subcommands arrive in later steps."""

import argparse
import random
from collections.abc import Sequence

from blackjack.ai.base import Strategy
from blackjack.ai.baseline import BaselineStrategy
from blackjack.ai.rule_based import RuleBasedStrategy
from blackjack.ui.console import play_game

AI_STRATEGIES: dict[str, type] = {
    "rule-based": RuleBasedStrategy,
    "baseline": BaselineStrategy,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="blackjack", description="Blackjack with AI players.")
    sub = parser.add_subparsers(dest="command", required=True)

    play = sub.add_parser("play", help="play a round against the dealer alongside an AI")
    play.add_argument("--ai", choices=sorted(AI_STRATEGIES), default="rule-based",
                      help="strategy for the AI player (default: rule-based)")
    play.add_argument("--seed", type=int, default=None, help="seed the deck shuffle")
    return parser


def cli(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.command == "play":
        ai: Strategy = AI_STRATEGIES[args.ai]()
        rng = random.Random(args.seed) if args.seed is not None else None
        play_game(ai, rng)
