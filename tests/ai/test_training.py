import random

from blackjack.ai.q_learning import QLearningAgent
from blackjack.ai.training import train, train_episode

# Win rates are statistical, so these tests only check mechanics and reproducibility.


def test_episode_returns_valid_reward():
    rng = random.Random(1)
    agent = QLearningAgent(rng=rng)
    assert all(train_episode(agent, rng) in (-1, 0, 1) for _ in range(50))


def test_episode_learns_something():
    rng = random.Random(1)
    agent = QLearningAgent(rng=rng)
    for _ in range(20):
        train_episode(agent, rng)
    assert agent.q_table
    assert any(v != 0.0 for q in agent.q_table.values() for v in q.values())


def test_result_counts_add_up():
    result = train(200, seed=3)
    assert result.games == 200
    assert 0.0 <= result.win_rate <= 1.0


def test_same_seed_gives_identical_q_table():
    assert train(300, seed=42).agent.q_table == train(300, seed=42).agent.q_table


def test_different_seeds_differ():
    assert train(300, seed=1).agent.q_table != train(300, seed=2).agent.q_table


def test_training_can_continue_an_existing_agent():
    first = train(100, seed=1)
    states_before = len(first.agent.q_table)
    train(100, seed=2, agent=first.agent)
    assert len(first.agent.q_table) >= states_before
