# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Implementation Summary

The system lives in `pawpal_system.py` and is built from four main classes, with a few small helper types. The UML is in `diagrams/uml.mmd`.

- **`Owner`** holds the owner's name, their daily available window (start and end time) and their pets. `get_all_tasks()` returns every pet's tasks together as `(pet, task)` pairs.
- **`Pet`** holds a name, a species and a list of tasks, with `add_task`, `edit_task` and `remove_task`. `edit_task` only allows the editable fields and validates the new values first, so a bad edit leaves the task unchanged.
- **`Task`** is one activity: a name, a fixed start time, a duration, a priority (`LOW`, `MEDIUM` or `HIGH`, default `MEDIUM`), a frequency (`ONCE`, `DAILY` or `WEEKLY`), a due date and a completed flag. `next_occurrence()` builds the next copy of a recurring task. It computes its own end time and checks whether it overlaps another task.
- **`Scheduler`** is the brain. It reads tasks only through `Owner.get_all_tasks()`, so it plans across all pets at once. It places tasks by priority, then earlier time, then the order they were created. A task that overlaps a higher-priority one is moved to the next free slot later in the day, or dropped if none exists. A task outside the owner's window is dropped. Each decision is recorded as a `PlanEntry`. `sort_by_time` and `filter_tasks` (by pet name or completion status) work on the `(pet, task)` pairs, and `complete_task` marks a task done and automatically adds the next occurrence of a daily or weekly task to its pet.
- **`PlanEntry`** is one line of the plan: the task, the pet's name, its final start time, an outcome (`KEPT`, `MOVED` or `DROPPED`) and the reason, which is what lets the plan explain itself.

How they work together: an `Owner` has `Pet`s, each `Pet` has `Task`s, and the `Scheduler` turns all of the owner's tasks into a list of `PlanEntry` objects.

**Status:** the classes, validation, sorting, filtering, recurring tasks, conflict detection, `build_plan()`, the `main.py` demo and 23 tests are done. `Pet.edit_task` and `Pet.remove_task` are implemented, and the Streamlit app can add pets and tasks, edit, remove or mark a task complete (which adds the next occurrence of a daily or weekly task), and generate the plan with its reasoning.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...

Today's Schedule for Jordan (07:00-20:00)
Time        | Pet Name | Activity       | Priority | Frequency
------------------------------------------------------------
07:30-08:00 | Rex      | Morning walk   | HIGH     | daily
08:00-08:10 | Mia      | Breakfast      | HIGH     | daily
12:30-12:50 | Mia      | Play session   | MEDIUM   | once
17:00-17:45 | Rex      | Grooming       | LOW      | weekly

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Orders `(pet, task)` pairs by start time, using task id to break ties. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name, completion status, or both. |
| Conflict detection | `Scheduler.find_conflicts()` | Returns warning messages for overlapping tasks, never an error. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Completing a daily or weekly task adds the next copy automatically. |
| Daily plan | `Scheduler.build_plan()` | Priority-first placement; moves or drops conflicting tasks and explains each decision. |

**Sorting.** `Scheduler.sort_by_time(pairs)` returns a new list of `(pet, task)` pairs sorted by `Task.start_time`, using `sorted()` with a lambda key of `(start_time, id)`. Two tasks at the same time keep their creation order, so the result is always the same. The input list is not changed.

**Filtering.** `Scheduler.filter_tasks(pet_name=None, completed=None)` reads every pet's tasks through `Owner.get_all_tasks()` and keeps only those that match. `pet_name="Rex"` keeps one pet's tasks, `completed=False` keeps pending tasks and `completed=True` keeps finished ones. A filter left as `None` is skipped, so the two can be combined. Its output feeds straight into `sort_by_time`.

**Conflict detection.** `Scheduler.find_conflicts()` is deliberately lightweight: it returns a list of warning strings instead of raising an error, so the program keeps running. An empty list means no conflicts.
- It compares tasks across all pets, so it catches an overlap on the same pet and between different pets. The message names the pets involved.
- A conflict is any overlap in time, not just an identical start. Two tasks that only touch (one ends exactly when the next starts) don't conflict.
- Completed tasks and tasks due on different days are ignored.
- The pending tasks are sorted by start time first, so each task is compared only with the tasks that start before it ends. The loop stops early after that, which keeps the check fast as the task list grows.

Example output from `main.py`:

```
Warning: Play session (12:30-12:50) overlaps Vet call (12:30-12:45) for Mia and Rex
Warning: Grooming (17:00-17:45) overlaps Training (17:15-17:45) for Rex
```

**Recurring tasks.** `Task.next_occurrence()` builds the next copy of a task. It's due today + 1 day for `DAILY` and today + 7 days for `WEEKLY`, calculated with `timedelta` so month ends, year ends and leap days are handled. `ONCE` tasks return `None`. `Scheduler.complete_task(pet, task)` marks the task complete and adds that copy to the pet, so the next occurrence is created automatically. Completing a task twice does not create a duplicate.

**Building the plan.** `Scheduler.build_plan(day=today)` combines these pieces into the daily plan. It takes the pending tasks due that day and places them by priority (high first), then earlier time, then creation order.
- A task outside the owner's window is **dropped** ("outside available window").
- A task that overlaps one already placed is **moved** to the next free slot later in the day, or **dropped** ("no free slot left in the day") if none fits before the window closes.
- Every entry is a `PlanEntry` with an outcome (`KEPT`, `MOVED` or `DROPPED`) and a plain-English reason. `Task` objects are never changed, so rebuilding the plan after an edit is always clean.

Example output from `main.py`:

```
Time        | Pet Name | Activity       | Priority | Outcome | Reason
07:30-08:00 | Rex      | Morning walk   | HIGH     | kept    | kept at requested time (priority HIGH)
12:30-12:45 | Rex      | Vet call       | HIGH     | kept    | kept at requested time (priority HIGH)
12:45-13:05 | Mia      | Play session   | MEDIUM   | moved   | moved from 12:30 to 12:45 because it overlapped Vet call
17:15-17:45 | Rex      | Training       | MEDIUM   | kept    | kept at requested time (priority MEDIUM)
17:45-18:30 | Rex      | Grooming       | LOW      | moved   | moved from 17:00 to 17:45 because it overlapped Training

Dropped
06:00  Rex   Early meds     outside available window (07:00-20:00)
```

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
