import pytest

from blackjack.cli import cli


def feed_inputs(monkeypatch, *answers: str):
    queue = list(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": queue.pop(0))
    return queue


def test_play_stand_prints_results(monkeypatch, capsys):
    feed_inputs(monkeypatch, "stand")
    cli(["play", "--seed", "1"])
    out = capsys.readouterr().out
    assert "Initial Deal" in out
    assert "Player stands." in out
    assert "Final Results" in out
    assert "Player vs Dealer:" in out
    assert "AI vs Dealer:" in out


def test_invalid_input_reprompts(monkeypatch, capsys):
    queue = feed_inputs(monkeypatch, "maybe", "STAND")
    cli(["play", "--seed", "1"])
    assert "Please enter Hit or Stand." in capsys.readouterr().out
    assert queue == []


def test_player_can_hit_until_bust(monkeypatch, capsys):
    feed_inputs(monkeypatch, *["hit"] * 20)
    cli(["play", "--seed", "3"])
    assert "Player busts" in capsys.readouterr().out


def test_same_seed_same_game(monkeypatch, capsys):
    feed_inputs(monkeypatch, "stand")
    cli(["play", "--seed", "5"])
    first = capsys.readouterr().out
    feed_inputs(monkeypatch, "stand")
    cli(["play", "--seed", "5"])
    assert capsys.readouterr().out == first


def test_baseline_ai_option(monkeypatch, capsys):
    feed_inputs(monkeypatch, "stand")
    cli(["play", "--ai", "baseline", "--seed", "1"])
    assert "Final Results" in capsys.readouterr().out


def test_unknown_ai_is_rejected():
    with pytest.raises(SystemExit):
        cli(["play", "--ai", "nope"])
