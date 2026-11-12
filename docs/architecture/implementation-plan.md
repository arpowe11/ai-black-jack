# Implementation Plan: Notebook to Codebase

This plan turns `ai_black_jack_game.ipynb` into the package described in [project-structure.md](project-structure.md). It follows the migration order from that document, with each layer verified by tests before the next one depends on it.

## Status

The scaffold exists (all files are created but empty). The original notebook is in place at `notebooks/archive/ai_black_jack_game.ipynb` (69 cells, 0-indexed); the cell numbers below refer to it.

## Step 0: Prep

- [x] Place the original notebook in `notebooks/archive/ai_black_jack_game.ipynb`, untouched.
- [x] Fill in `pyproject.toml` (name `blackjack-ai`, Python >= 3.11, `dev` and `notebooks` extras, `blackjack` script entry point).
- [x] Create a venv and run `pip install -e ".[dev]"`.
- [x] Add `src/blackjack/__init__.py` and `__main__.py` (calls `cli.main()`).

## Step 1: Game layer (`game/`)

Ported together with tests so the base layer is verified first.

- [x] `cards.py`: `create_deck(rng)` and card values (cell 5). Use dicts first; typed `Card`/`Rank`/`Suit` is a second pass.
- [x] `hand.py`: `calculate_score`, `has_usable_ace`, `is_bust` (cell 5).
- [x] `rules.py`: `Outcome` enum, a single `evaluate_outcome`, constants 21 and 17 (cells 11, 49).
- [x] `dealer.py`: `dealer_should_hit`, silent `play_dealer`. Replaces the three dealer versions (cells 7, 47, and `ai_turn` in 6).
- [x] `tests/conftest.py`: `hand()`, `stacked_deck()`, and seeded `rng` fixtures.
- [x] `tests/game/test_cards.py`, `test_hand.py`, `test_rules.py`, `test_dealer.py`.

**Done when:** `pytest tests/game` passes.

## Step 2: AI base and simple strategies (`ai/`)

- [x] `base.py`: `Action` enum, `GameState` dataclass (from cell 10 `get_game_state`), `Strategy` Protocol with `decide(state) -> Action`.
- [x] `baseline.py`: `BaselineStrategy` (cell 9).
- [x] `rule_based.py`: `RuleBasedStrategy` (cell 32, `get_ai_action_v2`; drop v1 from cell 19).
- [x] `tests/ai/test_baseline.py` and `test_rule_based.py`: print-and-check cells (8, 12-38) become parametrized asserts.

**Done when:** `pytest tests/ai/test_baseline.py tests/ai/test_rule_based.py` passes.

## Step 3: Engine, console UI, and `play`

- [x] `game/engine.py`: one `play_hand(strategy)` replacing `player_turn` and `ai_player_turn` (cells 6, 34), plus a round runner. No `print()`; return results or yield events.
- [x] `ui/console.py`: all `print()`/`input()` calls and `HumanStrategy`.
- [x] `cli.py`: `play` subcommand, matching the notebook's `main()` (cell 65).
- [x] `tests/integration/test_engine.py`: full rounds with stacked decks (cells 36-38).
- [x] `tests/integration/test_cli.py`: monkeypatched `input()`.

**Done when:** `blackjack play` behaves like the notebook's `main()` and integration tests pass.

## Step 4: Q-learning

- [ ] `ai/q_learning.py`: `QLearningAgent` class with `choose`, `update`, `save`, `load` (cells 42-46). Take `rng` and `epsilon` as constructor args. Serialize tuple keys as strings such as `"15,10,False"`.
- [ ] `ai/training.py`: `train_episode()` and `train(n, seed)` from v4 (cell 57). Drop v1-v3 and v4's redundant second `random.shuffle`.
- [ ] `tests/ai/test_q_learning.py`: update math (0.0 with reward 1 and learning rate 0.1 gives 0.1), `choose()` picks argmax at `epsilon=0`, save/load round trip.
- [ ] `tests/ai/test_training.py`: small deterministic smoke test. Do not assert win rates.
- [ ] Add `--ai q-learning` to `play`.
- [ ] Add `train` subcommand; run `blackjack train --seed 42` to produce `models/q_table.json`.

**Done when:** a seeded training run is reproducible and `blackjack play --ai q-learning` works.

## Step 5: Evaluation and `compare`

- [ ] `ai/evaluation.py`: `compare_strategies` (cells 60, 62).
- [ ] `cli.py`: add `compare` subcommand with `--seed`.

**Done when:** `blackjack compare --seed 42` gives the same output on every run.

## Step 6: Notebooks

New notebooks import only from `blackjack` and define no game logic.

- [ ] `01_game_walkthrough.ipynb`
- [ ] `02_q_learning_training.ipynb`
- [ ] `03_strategy_comparison.ipynb` (matplotlib chart from cell 63; requires the `notebooks` extra)

## Step 7: Docs

- [ ] `docs/index.md`
- [ ] `docs/architecture.md`: module map and how a round flows
- [ ] `docs/ai-strategies.md` (from cells 40-41)
- [ ] `docs/experiments/rule-vs-qlearning.md` (from cell 64, using the new seeded numbers; expect results to differ slightly from the original 44.6% vs 38.4%)
- [ ] `docs/contributors.md` (from cells 66-67)
- [ ] Update `README.md` with install and usage instructions

## Step 8: Final checks

- [ ] `ruff check .`
- [ ] `mypy src`
- [ ] `pytest`
- [ ] `python -m blackjack play` runs end to end
- [ ] Commit by layer so history mirrors the migration order

## Notebook-to-module quick reference

| Notebook cells | Destination |
|---|---|
| 5 | `game/cards.py`, `game/hand.py` |
| 10 | `ai/base.py` |
| 7, 47, `ai_turn` in 6 | `game/dealer.py` |
| 11, 49 | `game/rules.py` |
| 9 | `ai/baseline.py` |
| 32 | `ai/rule_based.py` |
| 6, 34 | `game/engine.py` + `ui/console.py` |
| 42-46 | `ai/q_learning.py` |
| 57 | `ai/training.py` |
| 60, 62 | `ai/evaluation.py` |
| 63 | `notebooks/03_strategy_comparison.ipynb` |
| 65 | `cli.py` |
| 8, 12-38, 48 | `tests/` |
| 40, 41, 64, 66, 67 | `docs/` |
