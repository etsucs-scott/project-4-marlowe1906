"""
save_manager.py
Handles reading and writing save data to a JSON file.

Demonstrates file I/O and exception handling: all disk operations are
wrapped in try/except so a missing or corrupted save never crashes the game.
"""

import json
import os
from typing import Any


class SaveManager:
    """
    Persists game progress (current level, coins, etc.) as JSON.

    Uses a dictionary internally so any serialisable value can be stored
    without changing the class interface.
    """

    # Keys expected in a valid save file
    _REQUIRED_KEYS: set[str] = {"level"}

    def __init__(self, filepath: str):
        """
        Args:
            filepath: Path to the JSON save file (e.g. 'saves/progress.json').
        """
        self.filepath = filepath
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save(self, data: dict[str, Any]) -> bool:
        """
        Write data to disk as JSON.

        Returns True on success, False if an error occurred.
        Never raises — failures are caught and reported to stdout.
        """
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError as e:
            print(f"[SaveManager] Could not write save file: {e}")
            return False

    def load(self) -> dict[str, Any]:
        """
        Read and parse the save file.

        Returns the stored dict on success, or a default dict on any error
        (missing file, bad JSON, wrong schema, etc.).
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Save data is not a JSON object.")
            self._validate(data)
            normalized = self._default()
            normalized.update(data)
            return normalized
        except FileNotFoundError:
            # First run — no save file yet
            return self._default()
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[SaveManager] Save file corrupt or invalid ({e}), using defaults.")
            return self._default()
        except OSError as e:
            print(f"[SaveManager] Could not read save file: {e}")
            return self._default()

    def reset(self) -> bool:
        """
        Delete the save file, effectively resetting progress.
        Returns True if deleted or already absent, False on error.
        """
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            return True
        except OSError as e:
            print(f"[SaveManager] Could not delete save file: {e}")
            return False

    def has_save(self) -> bool:
        """Return True if a save file currently exists on disk."""
        return os.path.isfile(self.filepath)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate(self, data: dict) -> None:
        """
        Raise KeyError if required keys are absent.
        Raise ValueError if values are out of expected ranges.
        """
        for key in self._REQUIRED_KEYS:
            if key not in data:
                raise KeyError(f"Missing required key: '{key}'")
        if not isinstance(data["level"], int) or data["level"] < 0:
            raise ValueError(f"Invalid level value: {data['level']}")
        if "coins" in data and (not isinstance(data["coins"], int) or data["coins"] < 0):
            raise ValueError(f"Invalid coin value: {data['coins']}")
        if "collected_coins" in data:
            collected = data["collected_coins"]
            if not isinstance(collected, dict):
                raise ValueError("Collected coin data must be a dictionary.")
            for level_key, coin_ids in collected.items():
                int(level_key)
                if not isinstance(coin_ids, list) or not all(isinstance(coin_id, str) for coin_id in coin_ids):
                    raise ValueError("Collected coin ids must be stored as string lists.")

    @staticmethod
    def _default() -> dict[str, Any]:
        """Return a fresh default save state."""
        return {"level": 0, "coins": 0, "collected_coins": {}}
