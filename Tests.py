"""
tests/test_all.py
Unit tests for the platformer project.
Run with: python -m pytest tests/ -v

Tests are grouped by class. pygame.init() is called once at module load
so that pygame.Rect and pygame.Surface are available without a display.
"""

import json
import os
import sys
import tempfile
import pytest

# Allow imports from the project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()  # Required before using pygame.Rect / Surface


# ===========================================================================
# Helpers
# ===========================================================================

def make_surface(w=924, h=690) -> pygame.Surface:
    """Return an off-screen surface that acts as a fake screen."""
    return pygame.Surface((w, h))


# ===========================================================================
# EventLog tests
# ===========================================================================

from game.event_log import EventLog


class TestEventLog:

    def test_push_and_len(self):
        log = EventLog(max_size=10)
        log.push("event one")
        log.push("event two")
        assert len(log) == 2

    def test_peek_returns_latest(self):
        log = EventLog(max_size=10)
        log.push("first")
        log.push("second")
        assert log.peek() == "second"

    def test_peek_empty_returns_none(self):
        log = EventLog(max_size=10)
        assert log.peek() is None

    def test_max_size_evicts_oldest(self):
        log = EventLog(max_size=3)
        log.push("a")
        log.push("b")
        log.push("c")
        log.push("d")   # "a" should be evicted
        assert len(log) == 3
        assert list(log)[0] == "b"

    def test_clear(self):
        log = EventLog(max_size=10)
        log.push("x")
        log.clear()
        assert len(log) == 0

    def test_pop_oldest(self):
        log = EventLog(max_size=10)
        log.push("first")
        log.push("second")
        oldest = log.pop_oldest()
        assert oldest == "first"
        assert len(log) == 1

    def test_invalid_max_size_raises(self):
        with pytest.raises(ValueError):
            EventLog(max_size=0)
        with pytest.raises(ValueError):
            EventLog(max_size=-5)

    def test_non_string_message_raises(self):
        log = EventLog()
        with pytest.raises(TypeError):
            log.push(42)

    def test_iteration_order(self):
        log = EventLog(max_size=10)
        msgs = ["alpha", "beta", "gamma"]
        for m in msgs:
            log.push(m)
        assert list(log) == msgs

    def test_repr(self):
        log = EventLog(max_size=5)
        log.push("hi")
        r = repr(log)
        assert "EventLog" in r
        assert "5" in r


# ===========================================================================
# SaveManager tests
# ===========================================================================

from game.save_manager import SaveManager


class TestSaveManager:

    def _tmp_path(self):
        """Return a unique temporary file path (file does not exist yet)."""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(path)   # we want the path only, not the file
        return path

    def test_save_and_load_roundtrip(self):
        path = self._tmp_path()
        sm = SaveManager(path)
        data = {"level": 2, "coins": 10}
        assert sm.save(data) is True
        loaded = sm.load()
        assert loaded["level"] == 2

    def test_load_returns_default_when_missing(self):
        sm = SaveManager("/tmp/nonexistent_xyz_abc.json")
        result = sm.load()
        assert result["level"] == 0

    def test_load_returns_default_on_corrupt_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write("NOT VALID JSON {{{")
        sm = SaveManager(path)
        result = sm.load()
        assert result["level"] == 0
        os.remove(path)

    def test_has_save_false_when_missing(self):
        sm = SaveManager("/tmp/definitely_not_here_xyz.json")
        assert sm.has_save() is False

    def test_has_save_true_after_save(self):
        path = self._tmp_path()
        sm = SaveManager(path)
        sm.save({"level": 0})
        assert sm.has_save() is True
        os.remove(path)

    def test_reset_removes_file(self):
        path = self._tmp_path()
        sm = SaveManager(path)
        sm.save({"level": 1})
        sm.reset()
        assert not os.path.exists(path)

    def test_load_rejects_negative_level(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"level": -3}, f)
        sm = SaveManager(path)
        result = sm.load()
        assert result["level"] == 0
        os.remove(path)


# ===========================================================================
# Player tests (headless — no display needed)
# ===========================================================================

from game.player import Player, GRAVITY, JUMP_VELOCITY


class TestPlayer:

    def _make_player(self):
        screen = make_surface()
        floor = [pygame.Rect(0, 626, 924, 64)]   # single ground tile row
        return Player(screen, floor), floor

    def test_initial_position(self):
        player, _ = self._make_player()
        assert player.rect.x == 60

    def test_check_on_map_true_when_visible(self):
        player, _ = self._make_player()
        assert player.check_on_map(924, 690) is True

    def test_check_on_map_false_when_fallen(self):
        player, _ = self._make_player()
        player.rect.y = 800   # below screen
        assert player.check_on_map(924, 690) is False

    def test_check_on_map_false_when_off_left(self):
        player, _ = self._make_player()
        player.rect.x = -100
        assert player.check_on_map(924, 690) is False

    def test_gravity_constant_positive(self):
        assert GRAVITY > 0

    def test_jump_velocity_negative(self):
        assert JUMP_VELOCITY < 0

    def test_reset_restores_position(self):
        player, floor = self._make_player()
        player.rect.x = 500
        player.rect.y = 200
        player.reset(floor)
        assert player.rect.x == 60


# ===========================================================================
# LevelManager tests
# ===========================================================================

from game.level_manager import LevelManager


class TestLevelManager:

    def test_starts_at_correct_level(self):
        screen = make_surface()
        lm = LevelManager(screen, start_level=0)
        assert lm.current_index == 0

    def test_get_floor_returns_list(self):
        screen = make_surface()
        lm = LevelManager(screen)
        floor = lm.get_current_floor()
        assert isinstance(floor, list)
        assert len(floor) > 0

    def test_next_level_advances_index(self):
        screen = make_surface()
        lm = LevelManager(screen, start_level=0)
        result = lm.next_level()
        assert result is True
        assert lm.current_index == 1

    def test_next_level_returns_false_at_end(self):
        screen = make_surface()
        lm = LevelManager(screen, start_level=0)
        lm.next_level()            # go to level 1
        result = lm.next_level()   # no level 2 — should be False
        assert result is False

    def test_total_levels(self):
        screen = make_surface()
        lm = LevelManager(screen)
        assert lm.total_levels() == 2

    def test_clamps_start_level(self):
        """start_level beyond registry bounds should clamp to last valid level."""
        screen = make_surface()
        lm = LevelManager(screen, start_level=99)
        assert lm.current_index == 1   # last valid index