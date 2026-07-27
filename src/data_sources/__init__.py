"""
data_sources - Base interface for any activity data source.

Any new source (GitHub, LeetCode, future ones) implements DataSource
and returns a SourceSnapshot. This is a generalization of the pattern
roast.py's get_github_activity() already used informally.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ActivityEvent:
    source: str
    timestamp: datetime
    title: str
    category: str
    metadata: dict = field(default_factory=dict)


@dataclass
class SourceSnapshot:
    events: List[ActivityEvent]
    streak_days: int
    total_count: int
    last_activity: Optional[datetime]
    categories: dict = field(default_factory=dict)
    extras: dict = field(default_factory=dict)


class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if this source is configured (has required env vars)."""
        ...

    @abstractmethod
    def fetch(self, since_iso: Optional[str] = None) -> SourceSnapshot:
        ...