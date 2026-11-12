import json
import random

import pytest

from blackjack.ai.base import Action, GameState
from blackjack.ai.q_learning import REWARDS, QLearningAgent
from blackjack.game.rules import Outcome

S = GameState(15, 10, False)
NEXT = GameState(18, 10, False)


def agent(**kwargs):
    kwargs.setdefault("rng", random.Random(0))
    return QLearningAgent(**kwargs)


def test_new_state_starts_at_zero():
    assert agent().values(S) == {Action.HIT: 0.0, Action.STAND: 0.0}


def test_update_from_zero_with_reward_one():
    a = agent(learning_rate=0.1)
    assert a.update(S, Action.HIT, 1) == pytest.approx(0.1)
    assert a.q_table[S][Action.HIT] == pytest.approx(0.1)
    assert a.q_table[S][Action.STAND] == 0.0


def test_update_uses_best_future_value():
    a = agent(learning_rate=0.5, discount_factor=0.9)
    a.q_table[NEXT] = {Action.HIT: 0.2, Action.STAND: 1.0}
    # 0 + 0.5 * (0 + 0.9 * 1.0 - 0) = 0.45
    assert a.update(S, Action.HIT, 0, NEXT) == pytest.approx(0.45)


def test_repeated_updates_converge_toward_reward():
    a = agent(learning_rate=0.1)
    for _ in range(200):
        a.update(S, Action.STAND, 1)
    assert a.q_table[S][Action.STAND] == pytest.approx(1.0, abs=1e-3)


def test_choose_without_exploration_picks_argmax():
    a = agent(epsilon=0.0)
    a.q_table[S] = {Action.HIT: -0.4, Action.STAND: 0.3}
    assert all(a.choose(S) is Action.STAND for _ in range(20))
    a.q_table[S] = {Action.HIT: 0.5, Action.STAND: 0.3}
    assert all(a.choose(S) is Action.HIT for _ in range(20))


def test_choose_with_full_exploration_tries_both_actions():
    a = agent(epsilon=1.0)
    a.q_table[S] = {Action.HIT: 1.0, Action.STAND: -1.0}
    assert {a.choose(S) for _ in range(50)} == {Action.HIT, Action.STAND}


def test_decide_is_greedy_and_does_not_learn():
    a = agent()
    a.q_table[S] = {Action.HIT: 0.5, Action.STAND: 0.1}
    assert a.decide(S) is Action.HIT
    assert a.q_table == {S: {Action.HIT: 0.5, Action.STAND: 0.1}}


def test_decide_stands_on_unknown_or_tied_state():
    a = agent()
    assert a.decide(S) is Action.STAND
    assert S not in a.q_table                      # decide never creates entries
    a.q_table[S] = {Action.HIT: 0.2, Action.STAND: 0.2}
    assert a.decide(S) is Action.STAND


def test_rewards_map_outcomes():
    assert REWARDS == {Outcome.WIN: 1, Outcome.LOSS: -1, Outcome.TIE: 0}


def test_save_and_load_round_trip(tmp_path):
    a = agent()
    a.q_table[S] = {Action.HIT: 0.25, Action.STAND: -0.5}
    a.q_table[GameState(18, 6, True)] = {Action.HIT: 0.0, Action.STAND: 0.75}
    path = tmp_path / "nested" / "q.json"
    a.save(path)

    assert QLearningAgent.load(path).q_table == a.q_table


def test_saved_file_uses_string_keys(tmp_path):
    a = agent()
    a.q_table[S] = {Action.HIT: 0.25, Action.STAND: -0.5}
    path = tmp_path / "q.json"
    a.save(path)
    assert json.loads(path.read_text()) == {"15,10,False": {"hit": 0.25, "stand": -0.5}}


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        QLearningAgent.load(tmp_path / "missing.json")
