"""Tabular Q-learning agent for hit/stand decisions."""

import json
import random
from pathlib import Path

from blackjack.ai.base import Action, GameState
from blackjack.game.rules import Outcome

REWARDS = {Outcome.WIN: 1, Outcome.LOSS: -1, Outcome.TIE: 0}

QValues = dict[Action, float]


def _key(state: GameState) -> str:
    """JSON can't use tuples as object keys, so states are stored like "15,10,False"."""
    return f"{state.score},{state.dealer_value},{state.usable_ace}"


def _parse_key(key: str) -> GameState:
    score, dealer, ace = key.split(",")
    return GameState(int(score), int(dealer), ace == "True")


class QLearningAgent:
    """Learns Q(state, action) from game outcomes. Also usable as a Strategy.

    `choose` is epsilon-greedy and used while training. `decide` is purely greedy
    and never modifies the table, so it is the method used for play and evaluation.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.1,
        rng: random.Random | None = None,
    ) -> None:
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.rng = rng or random.Random()
        self.q_table: dict[GameState, QValues] = {}

    def values(self, state: GameState) -> QValues:
        """Q-values for `state`, creating a zeroed entry the first time it is seen."""
        if state not in self.q_table:
            self.q_table[state] = {Action.HIT: 0.0, Action.STAND: 0.0}
        return self.q_table[state]

    def update(
        self,
        state: GameState,
        action: Action,
        reward: float,
        next_state: GameState | None = None,
    ) -> float:
        """Q(s,a) += lr * (reward + discount * max Q(s') - Q(s,a)). Returns the new value."""
        q = self.values(state)
        future = max(self.values(next_state).values()) if next_state is not None else 0.0
        q[action] += self.learning_rate * (reward + self.discount_factor * future - q[action])
        return q[action]

    def choose(self, state: GameState) -> Action:
        """Epsilon-greedy: explore with probability epsilon, otherwise take the best action.

        Ties between equal Q-values are broken at random.
        """
        q = self.values(state)
        if self.rng.random() < self.epsilon:
            return self.rng.choice(list(Action))
        best = max(q.values())
        return self.rng.choice([a for a, v in q.items() if v == best])

    def decide(self, state: GameState) -> Action:
        """Greedy action without learning or exploration. Unknown or tied states stand."""
        q = self.q_table.get(state)
        if q is not None and q[Action.HIT] > q[Action.STAND]:
            return Action.HIT
        return Action.STAND

    def save(self, path: str | Path) -> None:
        data = {_key(s): {a.value: v for a, v in q.items()} for s, q in self.q_table.items()}
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True))

    @classmethod
    def load(cls, path: str | Path, **kwargs) -> "QLearningAgent":
        agent = cls(**kwargs)
        data = json.loads(Path(path).read_text())
        for key, q in data.items():
            agent.q_table[_parse_key(key)] = {Action(name): v for name, v in q.items()}
        return agent
