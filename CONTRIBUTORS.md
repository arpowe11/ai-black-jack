# Contributors

## Alexander Powell: game rules, dealer, and orchestration

- Card deck construction, card values, and the Ace-aware hand calculator (`game/cards.py`, `game/hand.py`).
- The dealer, who hits below 17 and stands on 17 or more, with bust detection (`game/dealer.py`).
- The baseline computer strategy (`ai/baseline.py`).
- The three-hand game loop of human player, AI player, and dealer, with a final side-by-side comparison against the dealer (originally `main()`, now `game/engine.py` and `cli.py`).
- The original notebook's test suite.

## Basma Hameid: AI player development and evaluation

- Human Hit/Stand/Bust handling and the game-outcome evaluator (`game/rules.py`).
- The rule-based AI with separate soft-hand and hard-hand rules (`ai/rule_based.py`, from `get_ai_action_v2`).
- The Q-learning agent: state representation, Q-value updates, action selection, training, and evaluation (`ai/q_learning.py`, `ai/training.py`).
- The strategy comparison, chart, and written interpretation (`ai/evaluation.py`, `notebooks/03_strategy_comparison.ipynb`, `docs/experiments/`).
- AI decision tests, game-state tests, and the AI documentation.

## Migration from notebook to package

The original notebook is preserved in [`notebooks/archive/`](notebooks/archive/ai_black_jack_game.ipynb). It was restructured into this package following [docs/architecture/implementation-plan.md](docs/architecture/implementation-plan.md): duplicate dealers, outcome functions, and training versions were merged, global state became a class, and randomness became seedable.
