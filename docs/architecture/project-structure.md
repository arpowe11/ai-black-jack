# Project Structure: Blackjack AI

This document proposes how to turn `ai_black_jack_game.ipynb` into an installable Python project with separate modules for game logic, AI strategies, tests, docs, and notebooks.

## Current state of the notebook

The core logic is solid, but the notebook has accumulated duplication that the new structure should collapse rather than just relocate:

- Three dealer implementations: `dealer_turn`, `training_dealer_turn`, and the legacy `ai_turn`.
- Two functions that compute the same outcome in different types: `evaluate_game_winner` returns strings and `calculate_ai_reward` returns ints.
- Four versions of `train_one_game` (only v4 is current) and two versions of `get_ai_action` (only v2 is used).
- Q-learning state held in module globals, with `exploration_rate` toggled by hand for tests.
- Tests written as print-and-check cells instead of assertions.
- Unseeded randomness, so the documented experiment results can't be reproduced.

## Project layout

```
blackjack-ai/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   └── blackjack/
│       ├── __init__.py
│       ├── __main__.py            # enables `python -m blackjack`
│       ├── cli.py                 # argparse: play / train / compare subcommands
│       ├── game/
│       │   ├── __init__.py
│       │   ├── cards.py           # Card, Rank, Suit, create_deck(rng), card_value()
│       │   ├── hand.py            # calculate_score(), has_usable_ace(), is_bust()
│       │   ├── rules.py           # Outcome enum, evaluate_outcome(), constants (21, 17)
│       │   ├── dealer.py          # dealer_should_hit(), play_dealer()  ← one dealer, not three
│       │   └── engine.py          # deal + play a round; pure logic, emits events, no print()
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── base.py            # Action enum, GameState dataclass, Strategy Protocol
│       │   ├── baseline.py        # get_baseline_computer_action → BaselineStrategy
│       │   ├── rule_based.py      # get_ai_action_v2 → RuleBasedStrategy
│       │   ├── q_learning.py      # QLearningAgent class (table, choose, update, save/load)
│       │   ├── training.py        # train_one_game_v4 → train_episode(), train(n, seed)
│       │   └── evaluation.py      # play_comparison_game → compare_strategies()
│       └── ui/
│           ├── __init__.py
│           └── console.py         # all print()/input(); HumanStrategy lives here
├── models/
│   └── q_table.json               # trained Q-table (or .gitignore it and regenerate)
├── tests/
│   ├── conftest.py                # fixtures: hand("A", "7"), stacked_deck([...]), seeded rng
│   ├── game/
│   │   ├── test_cards.py
│   │   ├── test_hand.py
│   │   ├── test_rules.py
│   │   └── test_dealer.py
│   ├── ai/
│   │   ├── test_rule_based.py
│   │   ├── test_baseline.py
│   │   ├── test_q_learning.py
│   │   └── test_training.py
│   └── integration/
│       ├── test_engine.py         # full rounds with stacked decks
│       └── test_cli.py            # monkeypatched input()
├── docs/
│   ├── index.md
│   ├── architecture.md            # module map + how a round flows
│   ├── ai-strategies.md           # from notebook cells 40–41
│   ├── experiments/
│   │   └── rule-vs-qlearning.md   # from notebook cell 64 (Phase 6)
│   └── contributors.md            # from notebook cells 66–67
└── notebooks/
    ├── 01_game_walkthrough.ipynb
    ├── 02_q_learning_training.ipynb
    ├── 03_strategy_comparison.ipynb   # the matplotlib chart lives here
    └── archive/
        └── ai_black_jack_game.ipynb   # the original, untouched
```

## Design decisions

### `src/` layout

With the package under `src/`, tests can't import `blackjack` straight from the working directory; they must import the installed package (`pip install -e .`). This catches packaging mistakes, such as a missing `__init__.py` or forgotten data files, that a flat layout hides until someone else installs the project.

### One `Strategy` protocol for every player

`player_turn` and `ai_player_turn` are near-copies: loop, score, decide, draw, check bust. The only real difference is where the decision comes from. If the engine calls `strategy.decide(state) -> Action`, then `HumanStrategy` (which prompts via `input()`), `RuleBasedStrategy`, `BaselineStrategy`, and the Q-learning agent are all interchangeable, and there is a single `play_hand()` loop.

```python
class Strategy(Protocol):
    def decide(self, state: GameState) -> Action: ...
```

This also resolves the documented limitation that Q-learning "is not selectable in the main game." It becomes `blackjack play --ai q-learning`.

### No `print()` in `game/` or `ai/`

The engine either returns results or yields events, and `ui/console.py` renders them. This makes the code testable without capturing stdout, and it removes the reason `training_dealer_turn` existed: training needed a silent dealer. Once the dealer is silent by default, the duplicate goes away.

### One `Outcome` enum

`evaluate_game_winner` and `calculate_ai_reward` contain the same logic. Keep one function returning `Outcome.WIN`, `Outcome.LOSS`, or `Outcome.TIE`, and have the Q-learning code map it to a reward:

```python
REWARDS = {Outcome.WIN: 1, Outcome.LOSS: -1, Outcome.TIE: 0}
```

### `QLearningAgent` as a class, not globals

With `q_table`, `learning_rate`, and `exploration_rate` as module globals, every test shares and mutates the same state. That is why the notebook has to save and restore `exploration_rate` by hand. As a class, a test simply constructs `QLearningAgent(epsilon=0.0, rng=random.Random(0))`.

The class should also provide `save()` and `load()`. Note that the state keys are tuples, which JSON can't use as object keys, so serialize them as strings like `"15,10,False"` or as a list of `[state, values]` pairs.

### Pass an `rng` everywhere randomness happens

`create_deck()` currently calls the global `random.shuffle`, so the 135-state Q-table and the 44.6% vs 38.4% result can't be reproduced. If `create_deck(rng)`, `train(n, seed)`, and the agent's exploration all accept a `random.Random`, the experiment becomes rerunnable with `blackjack compare --seed 42`.

### Typed cards instead of dicts

A `@dataclass(frozen=True) class Card` with `Rank` and `Suit` enums turns typos like `card['rnak']` into errors caught by the type checker instead of `KeyError`s at runtime. This can be done as a second pass to keep the initial migration small; everything else works with dicts.

### Subcommands instead of a `scripts/` folder

`play`, `train`, and `compare` under one entry point means one thing to install and document. A folder of loose scripts tends to drift out of sync with the package.

## Notebook-to-module mapping

| Notebook cells | Destination | Notes |
|---|---|---|
| 5 (deck, values, score) | `game/cards.py`, `game/hand.py` | |
| 10 `get_game_state` | `ai/base.py` | Returns a `GameState` dataclass instead of a tuple |
| 7, 47, and `ai_turn` in 6 | `game/dealer.py` | Three implementations become one |
| 11, 49 | `game/rules.py` | Two outcome functions become one enum-returning function |
| 9 | `ai/baseline.py` | |
| 32 `get_ai_action_v2` | `ai/rule_based.py` | Drop v1 (cell 19) |
| 6 `player_turn`, 34 `ai_player_turn` | `game/engine.py` + `ui/console.py` | Merged into one `play_hand(strategy)` |
| 42–46 | `ai/q_learning.py` | Rewritten as a class |
| 57 (v4) | `ai/training.py` | Drop v1–v3; also drop v4's redundant second `random.shuffle` |
| 60, 62 | `ai/evaluation.py` | |
| 63 (chart) | `notebooks/03_strategy_comparison.ipynb` | |
| 65 `main()` | `cli.py` | |
| 8, 12–38, 48 (print tests) | `tests/` | Converted to pytest |
| 40, 41, 64, 66, 67 | `docs/` | |

## Testing approach

Most print-and-check cells become one parametrized test each. This keeps every case while making pytest report exactly which one failed:

```python
@pytest.mark.parametrize("score, dealer, soft, expected", [
    (10, 6, False, Action.HIT),
    (15, 6, False, Action.STAND),
    (15, 10, False, Action.HIT),
    (12, 2, False, Action.HIT),
    (18, 10, True, Action.HIT),
    (20, 10, False, Action.STAND),
])
def test_rule_based(score, dealer, soft, expected):
    assert RuleBasedStrategy().decide(GameState(score, dealer, soft)) == expected
```

The stacked-deck tests (cells 36–38, which hand-build a one-card deck) become integration tests. A `stacked_deck` fixture in `conftest.py` keeps them short.

For Q-learning, test the update math deterministically. For example, one update from 0.0 with reward 1 and learning rate 0.1 should give 0.1, and `choose()` with `epsilon=0` should pick the argmax. Win rates should not be asserted in tests because they are statistical; they belong in the experiment notebook and docs.

## `pyproject.toml` essentials

```toml
[project]
name = "blackjack-ai"
requires-python = ">=3.11"
dependencies = []                      # the game itself needs nothing

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
notebooks = ["jupyter", "matplotlib"]

[project.scripts]
blackjack = "blackjack.cli:main"
```

`matplotlib` stays out of the core dependencies on purpose. Only the comparison notebook uses it, so someone who just wants to play shouldn't have to install it.

## Notebook conventions

New notebooks should only import from `blackjack` and never define game logic. This rule keeps the project from turning back into one large notebook. The original notebook stays in `notebooks/archive/` so the team's history and documented results remain attached to the code that produced them.

## Migration order

1. Move `game/` first and port its tests, so the base layer is verified before anything depends on it.
2. Add `ai/base.py` and the rule-based and baseline strategies.
3. Build `engine.py` and `console.py` until `blackjack play` matches the notebook's `main()`.
4. Rewrite Q-learning as a class with a seeded RNG, retrain, and save `models/q_table.json`.
5. Rerun the comparison with a fixed seed and update `docs/experiments/`. Expect slightly different numbers than the original 44.6% vs 38.4%, since the original run wasn't seeded.