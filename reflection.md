# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My UML has four main classes, plus a small result class and an enum:

- **Owner:** holds the owner's name, their daily available window (start and end time) and their pets. It can add a pet, and `get_all_tasks()` returns every pet's tasks together as (pet, task) pairs. The scheduler reads tasks only through that method.
- **Pet:** holds a name, a species and its tasks. It can add, edit and remove tasks.
- **Task:** holds a name, a fixed start time, a duration, a priority (Low, Medium or High, default Medium), a frequency (once, daily or weekly), a due date, a completed flag and a creation timestamp. Completed tasks are skipped by the scheduler, and completing a daily or weekly task through `Scheduler.complete_task` automatically adds the next occurrence to the pet. It computes its own end time and checks whether it overlaps another task.
- **Scheduler:** reads the owner's pets' tasks and builds the daily plan. It orders tasks by priority, then time, then creation order, resolves overlaps and window limits, and records the reason for each decision.
- **PlanEntry:** one line of the plan, with the task, pet name, final start time, outcome (kept, moved or dropped) and reason. It's what lets the plan explain itself.
- **Priority (enum):** Low, Medium and High.

Owners have pets, pets have tasks, and the scheduler reads from the owner and produces plan entries.

The requirements the design is built around:

1. A user can assign each task a priority of Low, Medium or High (default: Medium). The scheduler places higher-priority tasks first. When the day can't fit everything, lower-priority tasks are dropped first, and the plan lists each dropped task with the reason. Ties within the same priority go to the task with the earlier scheduled time. If the times are also equal, the task that was logged first goes first.
2. A user can add tasks with a name, a fixed start time, a duration and a priority. End time is computed as start time plus duration. The scheduler detects when two tasks overlap in time. When there's a conflict, the higher-priority task keeps its slot. The lower-priority task is moved to the next free slot later in the day, or dropped if there isn't one, and the plan explains either outcome. A task must fit entirely inside the owner's available window. A task that starts before the window, or can't fit before it closes, is dropped with the reason "outside available window". A task that starts inside the window but overlaps a higher-priority task is moved or dropped as described above. Equal-priority conflicts use the same tie-break as item 1.
3. A user can enter owner info (name and daily available window, a start and end time) and add one or more pets (name and species). Each task belongs to a pet. A user can add, edit or remove a task, and the plan regenerates from the updated list.
4. A user can view a generated daily plan, ordered by start time. Each entry shows the pet, task, start time, duration and priority. Beside it, the plan explains why each task was kept, moved or dropped. Dropped tasks are listed separately with their reason.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design changed while I was tightening the requirements, before any scheduling code was written:

1. **`Priority` became an attribute of `Task` instead of its own class.** Priority is a value the user picks, so there is nothing for a class to classify. Making it an attribute (an enum with Low, Medium and High) keeps the design at four main classes, and the scheduler just sorts by it.
2. **I dropped the separate "Schedule a task" object.** The name and time live on `Task`, and the scheduling logic lives in `Scheduler`. `Task` also gained a fixed start time and a duration, with end time computed, so the scheduler can detect overlaps.
3. **I added `PlanEntry` and dropped a `Plan` wrapper.** The plan has to explain why each task was kept, moved or dropped, so each entry carries an outcome and a reason. A `Plan` class would have been a wrapper around two lists, so `Scheduler` holds those lists directly.
4. **`Owner` gained a daily available window.** Without it, "the day can't fit everything" and "moved to a later slot" have no meaning, because the day would never end.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler places tasks greedily in priority order and never reshuffles a higher-priority task to make room for a lower one. A high-priority task always keeps its slot, and any lower-priority task that overlaps it is moved to the next free slot later in the day or dropped. The cost is that this may not keep the most tasks possible. In some cases, moving the high-priority task or letting a lower-priority task win would have let two or three other tasks fit instead of dropping them. Finding that best arrangement means trying many combinations of tasks, which is much more complex to build, test and explain.

This is reasonable for pet care because the priorities mean something real: a medication or feeding must happen, and a play session can wait. The plan is also easy to predict and to explain. Each decision is one sentence ("moved because it overlapped a higher-priority task"), which matters since the plan has to show its reasoning. A day has a few dozen tasks, so the simple rule is good enough, and the user can always edit a task's time or priority if they disagree with the result.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
