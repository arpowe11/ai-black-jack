# AI strategies

Every strategy implements `decide(state: GameState) -> Action`, where the state is what a player can see:

| Field | Meaning |
|---|---|
| `score` | The player's current total |
| `dealer_value` | Value of the dealer's face-up card (10 for face cards, 11 for an Ace) |
| `usable_ace` | True if the player holds an Ace currently counted as 11 (a "soft" hand) |

## Baseline (`ai/baseline.py`)

Hit below 17, stand on 17 or more. It ignores the dealer's card and soft hands. This mirrors the dealer's own rule and serves as the reference point.

## Rule-based (`ai/rule_based.py`)

A simplified basic-strategy table.

Soft hand (usable Ace; one more card cannot bust it):
- 17 or less: hit
- 18: hit if the dealer shows 9 or higher, otherwise stand
- 19 or more: stand

Hard hand:
- 11 or less: hit
- 12: stand if the dealer shows 4, 5, or 6, otherwise hit
- 13 to 16: stand if the dealer shows 2 to 6, otherwise hit
- 17 or more: stand

The idea: when the dealer shows a weak card (2 to 6) they are likely to bust, so the player stands on a mediocre total rather than risk busting first. Against a strong card (7 or higher) the player keeps hitting.

## Q-learning (`ai/q_learning.py`, `ai/training.py`)

A tabular agent that learns hit/stand values from experience instead of being given rules.

**State.** The same `GameState` (score, dealer card, soft hand). Only states seen in training are stored, about 260 in practice.

**Update.** After each decision:

```
Q(s, a) += learning_rate * (reward + discount * max Q(s', a') - Q(s, a))
```

with `learning_rate = 0.1` and `discount = 0.9`. Hitting into a non-terminal hand gets reward 0 and bootstraps from the next state. Busting gives -1, and standing or reaching 21 gives the result against the dealer (+1 win, -1 loss, 0 tie, via `REWARDS`).

**Exploration.** While training, `choose` picks a random action with probability `epsilon = 0.1`, otherwise the best-valued action (ties broken at random).

**Playing.** `decide` is purely greedy and never changes the table. Unseen or tied states stand.

**Training.** `train(games, seed)` plays AI-versus-dealer games, updating the agent after every decision. The same seed reproduces the same Q-table. Use `blackjack train` to write `models/q_table.json`; `blackjack play --ai q-learning` loads it.

**Persistence.** `save` and `load` use JSON. Tuple states cannot be JSON keys, so they are stored as strings such as `"15,10,False"`.

## Limitations

- The rule-based strategy follows fixed rules and does not learn.
- The Q-learning state ignores the number of cards held and the cards already seen, and rewards come only at the end of a hand.
- Only hit and stand exist. There are no doubles, splits, insurance, or natural-blackjack payouts, and the dealer stands on soft 17.
- The tests cover the cases exercised; they do not prove every possible state is handled well.

For measured results, see [the experiment write-up](../experiments/rule-vs-qlearning.md).
