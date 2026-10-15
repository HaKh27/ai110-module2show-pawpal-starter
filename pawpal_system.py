from dataclasses import dataclass, field
from datetime import datetime, time
from enum import Enum
from itertools import count
from typing import List, Optional, Tuple

_task_ids = count(1)


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


class Outcome(Enum):
    KEPT = "kept"
    MOVED = "moved"
    DROPPED = "dropped"


def _minutes(t: time) -> int:
    """Return minutes since midnight for a time."""
    return t.hour * 60 + t.minute


@dataclass
class Task:
    name: str
    start_time: time
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    frequency: Frequency = Frequency.ONCE  # display only; the scheduler doesn't use it
    completed: bool = False
    id: int = field(default_factory=lambda: next(_task_ids))
    created_at: datetime = field(default_factory=datetime.now)  # display only; ties use id

    def __post_init__(self):
        """Validate priority, duration and that the task ends before midnight."""
        if not isinstance(self.priority, Priority):
            raise ValueError("priority must be a Priority")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        # Keep the task inside one day so end_time() never wraps past midnight.
        if _minutes(self.start_time) + self.duration_minutes >= 24 * 60:
            raise ValueError("task must end before midnight")

    def mark_complete(self) -> None:
        """Mark this task as done; the scheduler skips completed tasks."""
        self.completed = True

    def end_time(self) -> time:
        """Return start_time + duration_minutes."""
        end = _minutes(self.start_time) + self.duration_minutes
        return time(end // 60, end % 60)

    def overlaps(self, other: "Task") -> bool:
        """Return True if this task's time range overlaps other's."""
        # Back-to-back tasks (one ends exactly when the next starts) do not overlap.
        return (
            _minutes(self.start_time) < _minutes(other.end_time())
            and _minutes(other.start_time) < _minutes(self.end_time())
        )


@dataclass
class Pet:
    EDITABLE_FIELDS = ("name", "start_time", "duration_minutes", "priority", "frequency")

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        self.tasks.append(task)

    def edit_task(self, task_id: int, changes: dict) -> None:
        """Update the task with the given id using the given field changes."""
        # Only EDITABLE_FIELDS are allowed (raise ValueError otherwise);
        # re-run the Task checks after editing.
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

    def __post_init__(self):
        """Validate that the available window ends after it starts."""
        if self.window_end <= self.window_start:
            raise ValueError("window_end must be after window_start")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting duplicate pet names."""
        # Names must be unique because the plan identifies pets by name.
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"a pet named {pet.name!r} already exists")
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return every pet's tasks together as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class PlanEntry:
    task: Task
    pet_name: str
    final_start: Optional[time]  # None when the task is dropped
    outcome: Outcome
    reason: str


class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler for an owner with an empty plan."""
        self.owner = owner
        self.scheduled: List[PlanEntry] = []
        self.dropped: List[PlanEntry] = []

    def build_plan(self) -> None:
        """Rebuild the scheduled and dropped lists, with a reason on every entry."""
        # Read tasks only from self.owner.get_all_tasks(), skipping completed ones.
        # Place tasks in order of (-priority.value, start_time, id), resolving
        # overlaps and window limits. Then sort scheduled by final_start for display.
        self.scheduled.clear()
        self.dropped.clear()
        pass
