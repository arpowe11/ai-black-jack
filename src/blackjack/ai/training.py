"""Self-play training for the Q-learning agent (notebook's train_one_game_v4)."""

import random
from dataclasses import dataclass

from blackjack.ai.base import Action, get_game_state
from blackjack.ai.q_learning import REWARDS, QLearningAgent
from blackjack.game.cards import create_deck
from blackjack.game.dealer import play_dealer
from blackjack.game.hand import calculate_score
from blackjack.game.rules import BLACKJACK, evaluate_outcome


@dataclass
class TrainingResult:
    agent: QLearningAgent
    wins: int
    losses: int
    ties: int

    @property
    def games(self) -> int:
        return self.wins + self.losses + self.ties

    @property
    def win_rate(self) -> float:
        return self.wins / self.games if self.games else 0.0


def train_episode(agent: QLearningAgent, rng: random.Random | None = None) -> int:
    """Play one AI-vs-dealer game, updating `agent` after each decision.

    Returns the final reward: 1 win, -1 loss, 0 tie.
    """
    deck = create_deck(rng)
    ai_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    dealer_card = dealer_hand[0]

    def finish(score: int) -> int:
        play_dealer(deck, dealer_hand)
        return REWARDS[evaluate_outcome(score, calculate_score(dealer_hand))]

    while True:
        state = get_game_state(ai_hand, dealer_card)
        if state.score >= BLACKJACK:
            break

        action = agent.choose(state)
        if action is Action.STAND:
            reward = finish(state.score)
            agent.update(state, Action.STAND, reward)
            return reward

        if not deck:
            break
        ai_hand.append(deck.pop())
        new_state = get_game_state(ai_hand, dealer_card)

        if new_state.score > BLACKJACK:
            agent.update(state, Action.HIT, -1)
            return -1
        if new_state.score == BLACKJACK:
            reward = finish(new_state.score)
            agent.update(state, Action.HIT, reward)
            return reward

        agent.update(state, Action.HIT, 0, new_state)

    # Started on 21, or the deck ran out.
    return finish(calculate_score(ai_hand))


def train(
    games: int,
    seed: int | None = None,
    agent: QLearningAgent | None = None,
) -> TrainingResult:
    """Train for `games` episodes. The same seed reproduces the same Q-table."""
    rng = random.Random(seed)
    agent = agent or QLearningAgent(rng=rng)
    agent.rng = rng

    wins = losses = ties = 0
    for _ in range(games):
        reward = train_episode(agent, rng)
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            ties += 1
    return TrainingResult(agent, wins, losses, ties)
