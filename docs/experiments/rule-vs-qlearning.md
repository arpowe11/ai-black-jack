# Experiment: rule-based vs Q-learning

## Objective

Measure how often each strategy wins against the dealer: baseline, rule-based, and Q-learning.

## Method

- `compare_strategies` shuffles a deck with a seeded `random.Random`, then every strategy plays one hand against the dealer from a copy of that same deck (a paired comparison).
- Each strategy's hand is played solo against the dealer; the human player and the second AI are not involved.
- The Q-learning agent uses `decide`, which is greedy and never learns during evaluation.
- Q-table: `models/q_table.json`, trained with `blackjack train --games 50000 --seed 42` (260 states).
- Everything is reproducible: `blackjack compare --games 1000 --seed 42`.

Strategies can take different actions after the same starting deck, so their later cards (and game paths) can diverge. Pairing reduces noise from the opening deal but does not remove it.

## Results

### The standard run (1,000 games, seed 42)

| Metric | Baseline | Rule-based | Q-learning |
|---|---:|---:|---:|
| Wins | 390 | 426 | 425 |
| Losses | 508 | 483 | 489 |
| Ties | 102 | 91 | 86 |
| Win rate | 39.0% | 42.6% | 42.5% |

### Is that stable? Ten deck seeds (1,000 games each, same model)

| Strategy | Mean win rate | Std. dev. | Range |
|---|---:|---:|---|
| Baseline | 41.2% | 1.4 | 39.2 to 43.9 |
| Rule-based | 43.7% | 1.4 | 42.2 to 46.2 |
| Q-learning | 42.8% | 1.7 | 40.5 to 45.6 |

The standard run above (seed 42) happens to be a low draw for the baseline and an average one for the others. A single 1,000-game run moves by about 1.5 points either way, which is as large as the gap between rule-based and Q-learning.

### A large run (100,000 games, seed 42)

| Strategy | Wins | Losses | Ties | Win rate |
|---|---:|---:|---:|---:|
| Baseline | 40,910 | 48,969 | 10,121 | 40.9% |
| Rule-based | 43,308 | 47,522 | 9,170 | 43.3% |
| Q-learning | 42,277 | 49,394 | 8,329 | 42.3% |

### Does the training seed or amount matter? (evaluated on the same 100,000 games)

| Training | States | Win rate |
|---|---:|---:|
| 50,000 games, seeds 0 to 4 | 260 | 42.0% to 42.7% |
| 1,000 games | 217 | 40.9% |
| 10,000 games | 258 | 42.2% |
| 200,000 games | 260 | 42.8% |

## Interpretation

- Both rule-based and Q-learning clearly beat the baseline, by about 1.5 to 2.5 points in the 100,000-game run.
- Rule-based finishes ahead of Q-learning by about 1 point over a large sample (43.3% vs 42.3%). The gap is small, and a single 1,000-game run cannot reliably detect it.
- Q-learning approaches the rule-based strategy as it trains. It reaches roughly 42 to 43% after 10,000 games and stays there, so extra training beyond that adds little under this design.
- No strategy wins more than about 43% of hands. That is expected: the dealer has a structural advantage, and ties are not wins.

## Comparison with the original notebook

The original notebook reported 44.6% for rule-based and 38.4% for Q-learning (a 6.2-point gap) from a single unseeded 1,000-game run, with a Q-table of 135 states trained on a few hundred games. Those numbers cannot be reproduced because nothing was seeded. The new results differ for two reasons: the Q-learning agent is now trained much longer (260 states, 50,000 games), which closes most of the gap, and the multi-seed table above shows that a single 1,000-game run swings by more than a point or two. The conclusion that rule-based is at least as good as Q-learning holds; the conclusion that it is far better does not.

## Limitations

- Results apply to this project's rules: hit/stand only, dealer stands on all 17s, no blackjack payouts, win/loss/tie scoring.
- Q-learning's state ignores cards already seen; richer state or reward design might change the outcome.
- Training used fixed hyperparameters (`learning_rate=0.1`, `discount=0.9`, `epsilon=0.1`). Tuning them was not part of this experiment.
- The numbers above come from one model and a handful of seeds, not an exhaustive study.

## Reproducing

```bash
blackjack train --games 50000 --seed 42
blackjack compare --games 1000 --seed 42
```

The chart is in [`notebooks/03_strategy_comparison.ipynb`](../../notebooks/03_strategy_comparison.ipynb).
