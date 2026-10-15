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
- **`Pet`** holds a name, a species and a list of tasks, with `add_task`, `edit_task` and `remove_task`.
- **`Task`** is one activity: a name, a fixed start time, a duration, a priority (`LOW`, `MEDIUM` or `HIGH`, default `MEDIUM`), a frequency (`ONCE`, `DAILY` or `WEEKLY`, shown in the plan only) and a completed flag. It computes its own end time and checks whether it overlaps another task.
- **`Scheduler`** is the brain. It reads tasks only through `Owner.get_all_tasks()`, so it plans across all pets at once. It places tasks by priority, then earlier time, then the order they were created. A task that overlaps a higher-priority one is moved to the next free slot later in the day, or dropped if none exists. A task outside the owner's window is dropped. Each decision is recorded as a `PlanEntry`.
- **`PlanEntry`** is one line of the plan: the task, the pet's name, its final start time, an outcome (`KEPT`, `MOVED` or `DROPPED`) and the reason, which is what lets the plan explain itself.

How they work together: an `Owner` has `Pet`s, each `Pet` has `Task`s, and the `Scheduler` turns all of the owner's tasks into a list of `PlanEntry` objects.

**Status:** the classes, validation, `main.py` demo and first tests are done. `Scheduler.build_plan()`, `Pet.edit_task` and `Pet.remove_task` are still stubs, and the Streamlit UI isn't connected yet. `main.py` currently prints tasks sorted by start time as a placeholder for the real plan.

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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
