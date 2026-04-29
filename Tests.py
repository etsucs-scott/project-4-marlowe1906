"""
Tests.py
Unit tests for the platformer project.

Run with:
    python -m unittest Tests.py -q
"""

import json
import os
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from EventLog import EventLog
from LevelManager import LevelManager
from Main import _load_coin_progress, _serialize_coin_progress
from Player import GRAVITY, JUMP_VELOCITY, Player
from SaveManager import SaveManager


pygame.init()
pygame.display.set_mode((1, 1))


def make_surface(w=924, h=690) -> pygame.Surface:
    """Return an off-screen surface that acts as a fake screen."""
    return pygame.Surface((w, h))


class TestEventLog(unittest.TestCase):
    def test_push_and_len(self):
        log = EventLog(max_size=10)
        log.push("event one")
        log.push("event two")
        self.assertEqual(len(log), 2)

    def test_peek_returns_latest(self):
        log = EventLog(max_size=10)
        log.push("first")
        log.push("second")
        self.assertEqual(log.peek(), "second")

    def test_peek_empty_returns_none(self):
        log = EventLog(max_size=10)
        self.assertIsNone(log.peek())

    def test_max_size_evicts_oldest(self):
        log = EventLog(max_size=3)
        log.push("a")
        log.push("b")
        log.push("c")
        log.push("d")
        self.assertEqual(len(log), 3)
        self.assertEqual(list(log)[0], "b")

    def test_clear(self):
        log = EventLog(max_size=10)
        log.push("x")
        log.clear()
        self.assertEqual(len(log), 0)

    def test_pop_oldest(self):
        log = EventLog(max_size=10)
        log.push("first")
        log.push("second")
        oldest = log.pop_oldest()
        self.assertEqual(oldest, "first")
        self.assertEqual(len(log), 1)

    def test_invalid_max_size_raises(self):
        with self.assertRaises(ValueError):
            EventLog(max_size=0)
        with self.assertRaises(ValueError):
            EventLog(max_size=-5)

    def test_non_string_message_raises(self):
        log = EventLog()
        with self.assertRaises(TypeError):
            log.push(42)

    def test_iteration_order(self):
        log = EventLog(max_size=10)
        msgs = ["alpha", "beta", "gamma"]
        for message in msgs:
            log.push(message)
        self.assertEqual(list(log), msgs)

    def test_repr(self):
        log = EventLog(max_size=5)
        log.push("hi")
        representation = repr(log)
        self.assertIn("EventLog", representation)
        self.assertIn("5", representation)


class TestSaveManager(unittest.TestCase):
    def _tmp_path(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(path)
        return path

    def test_save_and_load_roundtrip(self):
        path = self._tmp_path()
        save_manager = SaveManager(path)
        data = {"level": 2, "coins": 10, "collected_coins": {"0": ["coin_0"]}}
        self.assertTrue(save_manager.save(data))
        loaded = save_manager.load()
        self.assertEqual(loaded["level"], 2)
        self.assertEqual(loaded["coins"], 10)
        self.assertEqual(loaded["collected_coins"], {"0": ["coin_0"]})
        os.remove(path)

    def test_load_returns_default_when_missing(self):
        path = self._tmp_path()
        save_manager = SaveManager(path)
        result = save_manager.load()
        self.assertEqual(result["level"], 0)
        self.assertEqual(result["coins"], 0)
        self.assertEqual(result["collected_coins"], {})

    def test_load_returns_default_on_corrupt_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("NOT VALID JSON {{{")
        save_manager = SaveManager(path)
        result = save_manager.load()
        self.assertEqual(result["level"], 0)
        self.assertEqual(result["coins"], 0)
        os.remove(path)

    def test_has_save_false_when_missing(self):
        path = self._tmp_path()
        save_manager = SaveManager(path)
        self.assertFalse(save_manager.has_save())

    def test_has_save_true_after_save(self):
        path = self._tmp_path()
        save_manager = SaveManager(path)
        save_manager.save({"level": 0})
        self.assertTrue(save_manager.has_save())
        os.remove(path)

    def test_reset_removes_file(self):
        path = self._tmp_path()
        save_manager = SaveManager(path)
        save_manager.save({"level": 1})
        save_manager.reset()
        self.assertFalse(os.path.exists(path))

    def test_load_rejects_negative_level(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump({"level": -3}, handle)
        save_manager = SaveManager(path)
        result = save_manager.load()
        self.assertEqual(result["level"], 0)
        os.remove(path)

    def test_load_rejects_negative_coins(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump({"level": 1, "coins": -1}, handle)
        save_manager = SaveManager(path)
        result = save_manager.load()
        self.assertEqual(result["coins"], 0)
        os.remove(path)


class TestPlayer(unittest.TestCase):
    def _make_player(self):
        screen = make_surface()
        floor = [pygame.Rect(0, 626, 924, 64)]
        return Player(screen, floor), floor

    def test_initial_position(self):
        player, _ = self._make_player()
        self.assertEqual(player.rect.x, 60)

    def test_check_on_map_true_when_visible(self):
        player, _ = self._make_player()
        self.assertTrue(player.check_on_map(924, 690))

    def test_check_on_map_false_when_fallen(self):
        player, _ = self._make_player()
        player.rect.y = 800
        self.assertFalse(player.check_on_map(924, 690))

    def test_check_on_map_false_when_off_left_on_first_level(self):
        player, _ = self._make_player()
        player.rect.x = -100
        self.assertFalse(player.check_on_map(924, 690))

    def test_check_on_map_allows_backtracking_on_later_levels(self):
        player, _ = self._make_player()
        player.rect.x = -10
        self.assertTrue(player.check_on_map(924, 690, level_index=1))

    def test_gravity_constant_positive(self):
        self.assertGreater(GRAVITY, 0)

    def test_jump_velocity_negative(self):
        self.assertLess(JUMP_VELOCITY, 0)

    def test_reset_restores_position(self):
        player, floor = self._make_player()
        player.rect.x = 500
        player.rect.y = 200
        player.reset(floor)
        self.assertEqual(player.rect.x, 60)


class TestLevelManager(unittest.TestCase):
    def test_starts_at_correct_level(self):
        screen = make_surface()
        level_manager = LevelManager(screen, start_level=0)
        self.assertEqual(level_manager.current_index, 0)

    def test_get_floor_returns_list(self):
        screen = make_surface()
        level_manager = LevelManager(screen)
        floor = level_manager.get_current_floor()
        self.assertIsInstance(floor, list)
        self.assertGreater(len(floor), 0)

    def test_get_coins_returns_list(self):
        screen = make_surface()
        level_manager = LevelManager(screen)
        coins = level_manager.get_current_coins()
        self.assertIsInstance(coins, list)
        self.assertGreater(len(coins), 0)

    def test_next_level_advances_index(self):
        screen = make_surface()
        level_manager = LevelManager(screen, start_level=0)
        result = level_manager.next_level()
        self.assertTrue(result)
        self.assertEqual(level_manager.current_index, 1)

    def test_next_level_returns_false_at_end(self):
        screen = make_surface()
        level_manager = LevelManager(screen, start_level=0)
        for _ in range(level_manager.total_levels() - 1):
            self.assertTrue(level_manager.next_level())
        self.assertFalse(level_manager.next_level())

    def test_previous_level_returns_false_at_start(self):
        screen = make_surface()
        level_manager = LevelManager(screen, start_level=0)
        self.assertFalse(level_manager.previous_level())

    def test_total_levels(self):
        screen = make_surface()
        level_manager = LevelManager(screen)
        self.assertEqual(level_manager.total_levels(), 5)

    def test_total_coin_count(self):
        screen = make_surface()
        level_manager = LevelManager(screen)
        self.assertGreater(level_manager.total_coin_count(), 0)

    def test_clamps_start_level(self):
        screen = make_surface()
        level_manager = LevelManager(screen, start_level=99)
        self.assertEqual(level_manager.current_index, 4)

    def test_collect_current_coins_updates_progress(self):
        screen = make_surface()
        level_manager = LevelManager(screen)
        first_coin = level_manager.get_current_coins()[0]
        collected_ids = level_manager.collect_current_coins(first_coin.rect)
        self.assertEqual(collected_ids, [first_coin.coin_id])
        self.assertIn(first_coin.coin_id, level_manager.collected_coins[0])

    def test_reloads_collected_coin_state(self):
        screen = make_surface()
        level_manager = LevelManager(screen, collected_coins={0: {"coin_0"}})
        first_coin = level_manager.get_current_coins()[0]
        self.assertTrue(first_coin.collected)


class TestCoinProgressHelpers(unittest.TestCase):
    def test_serialize_coin_progress(self):
        progress = {0: {"coin_1", "coin_0"}, 2: {"coin_4"}}
        result = _serialize_coin_progress(progress)
        self.assertEqual(result, {"0": ["coin_0", "coin_1"], "2": ["coin_4"]})

    def test_load_coin_progress(self):
        raw = {"0": ["coin_0", "coin_1"], "bad": ["coin_9"], "2": ["coin_4", 3]}
        result = _load_coin_progress(raw)
        self.assertEqual(result, {0: {"coin_0", "coin_1"}, 2: {"coin_4"}})


if __name__ == "__main__":
    unittest.main()
