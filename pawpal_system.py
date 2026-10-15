from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from itertools import count
from typing import List, Optional

_task_ids = count(1)


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    start_time: time
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    id: int = field(default_factory=lambda: next(_task_ids))
    created_at: datetime = field(default_factory=datetime.now)

    def end_time(self) -> time:
        """Return start_time + duration_minutes."""
        pass

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time range overlaps other's (back-to-back is not an overlap)."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        pass

    def edit_task(self, task_id: int, changes: dict) -> None:
        """Update the fields of the task with the given id."""
        pass

    def remove_task(self, task_id: int) -> None:
        """Remove the task with the given id."""
        pass


@dataclass
class Owner:
    name: str
    window_start: time
    window_end: time
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass


@dataclass
class PlanEntry:
    task: Task
    pet_name: str
    final_start: Optional[time]  # None when the task is dropped
    outcome: str  # "kept", "moved" or "dropped"
    reason: str


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.scheduled: List[PlanEntry] = []
        self.dropped: List[PlanEntry] = []

    def build_plan(self) -> None:
        """Sort by priority, then time, then created_at; resolve conflicts and window limits; fill scheduled and dropped with reasons."""
        pass
