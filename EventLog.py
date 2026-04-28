"""
event_log.py
A fixed-capacity event log backed by a collections.deque.

Satisfies the 'non-trivial data structure' requirement: a deque is used
as a bounded queue — old events are automatically discarded when the log
is full, giving O(1) push and O(1) eviction from the left.
"""

from collections import deque
from typing import Iterator


class EventLog:
    """
    Stores the most recent N game events as strings.

    Internally uses collections.deque with a maxlen so the oldest entries
    are dropped automatically when capacity is reached (queue semantics).

    Example:
        log = EventLog(max_size=5)
        log.push("Level started")
        log.push("Player jumped")
        list(log)   # ["Level started", "Player jumped"]
    """

    def __init__(self, max_size: int = 50):
        """
        Args:
            max_size: Maximum number of events retained. Must be > 0.
        Raises:
            ValueError: If max_size is not a positive integer.
        """
        if not isinstance(max_size, int) or max_size <= 0:
            raise ValueError(f"max_size must be a positive integer, got {max_size!r}")
        self._log: deque[str] = deque(maxlen=max_size)
        self.max_size = max_size

    def push(self, message: str) -> None:
        """
        Append a new event message.
        If the log is at capacity the oldest message is silently discarded.
        """
        if not isinstance(message, str):
            raise TypeError(f"Event message must be a str, got {type(message).__name__}")
        self._log.append(message)

    def peek(self) -> str | None:
        """Return the most recent event without removing it, or None if empty."""
        return self._log[-1] if self._log else None

    def pop_oldest(self) -> str | None:
        """Remove and return the oldest event (left side of the deque), or None."""
        return self._log.popleft() if self._log else None

    def clear(self) -> None:
        """Remove all events."""
        self._log.clear()

    def __len__(self) -> int:
        return len(self._log)

    def __iter__(self) -> Iterator[str]:
        """Iterate from oldest to newest."""
        return iter(self._log)

    def __repr__(self) -> str:
        return f"EventLog(max_size={self.max_size}, entries={len(self._log)})"