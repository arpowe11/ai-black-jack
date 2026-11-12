# Blackjack AI

A command-line Blackjack game where a human and an AI player each play against the dealer. The AI can use a baseline rule, a rule-based strategy, or a Q-learning agent trained by self-play. The package also includes tools to train and compare the strategies reproducibly.

Penn State, Foundations of AI, final project. See [CONTRIBUTORS.md](CONTRIBUTORS.md).

## Install

Requires Python 3.11 or newer. The game itself has no dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"          # add ",notebooks" for Jupyter and matplotlib
```

## Usage

Play a round (you and the AI against the dealer):

```bash
blackjack play                          # rule-based AI
blackjack play --ai baseline            # hit below 17, otherwise stand
blackjack play --ai q-learning          # uses models/q_table.json
blackjack play --seed 7                 # reproducible shuffle
```

Train the Q-learning agent and save its Q-table:

```bash
blackjack train --games 50000 --seed 42
```

Compare all three strategies on identical decks:

```bash
blackjack compare --games 1000 --seed 42
```

`python -m blackjack ...` works too.

## Rules implemented

Standard hit/stand Blackjack against a dealer who hits below 17 and stands on 17 or more (including soft 17). Aces count 11 unless that would bust the hand. There are no splits, doubles, insurance, or natural-blackjack payouts. The result for each player is win, loss, or tie against the dealer.

## Project layout

```
src/blackjack/
  game/    cards, hand scoring, rules, dealer, round engine (no printing)
  ai/      Strategy protocol, baseline, rule-based, Q-learning, training, evaluation
  ui/      console input and output
  cli.py   play / train / compare
tests/     pytest suite (unit and integration)
notebooks/ walkthrough, training, and comparison notebooks; the original is in archive/
docs/      architecture, strategies, experiment write-up
models/    trained Q-table
```

## Development

```bash
pytest          # run the test suite
ruff check .    # lint
mypy src        # type check
```

## Documentation

Start at [docs/index.md](docs/index.md).
