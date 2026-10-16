# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My UML has four main classes, plus a small result class and three enums:

- **Owner:** holds the owner's name, their daily available window (start and end time) and their pets. It can add a pet, and `get_all_tasks()` returns every pet's tasks together as (pet, task) pairs. The scheduler reads tasks only through that method.
- **Pet:** holds a name, a species and its tasks. It can add, edit and remove tasks.
- **Task:** holds a name, a fixed start time, a duration, a priority (Low, Medium or High, default Medium), a frequency (once, daily or weekly), a due date, a completed flag and a creation timestamp. Completed tasks are skipped by the scheduler, and completing a daily or weekly task through `Scheduler.complete_task` automatically adds the next occurrence to the pet. It computes its own end time and checks whether it overlaps another task.
- **Scheduler:** reads the owner's pets' tasks and builds the daily plan. It orders tasks by priority, then time, then creation order, resolves overlaps and window limits, and records the reason for each decision.
- **PlanEntry:** one line of the plan, with the task, pet name, final start time, outcome (kept, moved or dropped) and reason. It's what lets the plan explain itself.
- **Priority, Frequency and Outcome (enums):** Low, Medium and High; once, daily and weekly; and kept, moved and dropped.

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

Later changes came from building and testing the code, and I updated the UML to match at the end:

5. **`Task` gained an `id`, a `due_date` and a `Frequency`.** The id gives a stable tie-break and lets `edit_task` and `remove_task` find a task. The due date and frequency let a completed daily or weekly task create its next copy without the plan mixing days.
6. **`Scheduler` gained `sort_by_time`, `filter_tasks`, `find_conflicts` and `complete_task`.** The UI and the plan both needed sorted, filtered views, and conflicts had to be reported as warnings instead of errors.
7. **A plan never changes a `Task`.** A moved time lives in `PlanEntry.final_start`, so rebuilding the plan after an edit always starts clean.
8. **The UML had drifted slightly.** At the end I checked it against `pawpal_system.py` and added the pieces it was missing: `Pet.EDITABLE_FIELDS`, `Pet._find_task` and `Scheduler._drop`.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers four constraints:
- **The owner's daily window.** Tasks must fit entirely between the owner's start and end time, or they are dropped. This is the only hard limit.
- **Time and overlaps.** Every task has a fixed start time and a duration, and two tasks can't overlap. Overlaps are resolved rather than allowed.
- **Priority.** Each task is Low, Medium or High (default Medium), and it decides who keeps a slot in a conflict.
- **Task status and date.** Only pending tasks due that day are planned, so completed tasks and tomorrow's recurring copies stay out of today's plan.

I put the window first, because a plan that runs outside the hours the owner is available is useless. Priority comes next, ahead of time, because in pet care the importance of a task matters more than when it was asked for: a medication or feeding must happen, while a play session can move. Time is the tie-breaker, with the earlier task winning and creation order deciding any remaining tie. I left out owner preferences and flexible time windows on purpose. They add a lot of complexity, and the fixed times plus priorities already cover the main scenario.

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

I used an AI coding assistant (Claude Code) for almost every stage:
- **Design brainstorming.** I gave it my three rough requirements and we tightened them one at a time. It proposed wording and asked questions (for example, how a conflict should be resolved), and I approved each change before it was written.
- **UML.** It drafted the Mermaid class diagram, and I trimmed it.
- **Skeleton and review.** It generated the class skeleton with dataclasses, then reviewed it for missing relationships and logic risks before any scheduling code existed.
- **Implementation.** It wrote sorting, filtering, conflict detection, recurring tasks, `build_plan()` and the Streamlit wiring.
- **Debugging and refactoring.** For example, it found why adding a task from the UI silently did nothing, and it simplified the conflict check.
- **UI and docs.** It added the pet and status filters and the custom species box to the Streamlit app, checked the UML against the final code, and drafted the README's Features list and Demo Walkthrough, which I reviewed and corrected.
- **Tests.** It drafted the pytest tests, and we ran them after each step.

The most helpful prompts were specific and asked for a judgment. "Do you think this has too much going on, or is it just right according to the requirements?" and "if anything is redundant work, simplify it" led to real simplifications. "Review the skeleton for missing relationships or potential logic bottlenecks" caught problems early, such as the plan being duplicated on rebuild and tasks wrapping past midnight. Working one step at a time and approving each change before it was made kept me in control of the design.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The first UML draft the AI gave me had a separate `Plan` class that held the scheduled and dropped lists, plus `PlanEntry` for each line of the plan. I asked whether that was too complicated for the requirements. Looking at it again, `Plan` was only a wrapper around two lists, so I told it to drop `Plan` and keep `PlanEntry`, and the scheduler now holds the lists itself. I kept `PlanEntry` because the plan has to explain each decision. I made a similar call on the tie-break rule: the AI's wording was ambiguous about what "logged first" meant, so I specified it myself (earlier time first, then creation order).

I didn't take the AI's work on trust once it was written. I ran every change: the `main.py` demo, the pytest suite, and a Streamlit test run of the real app. Those runs caught a real bug. Streamlit's pet dropdown returns a copy of the pet object, so tasks added from the UI were silently going to a throwaway copy. The AI's own first benchmark of the conflict check was also unfair, because it compared different amounts of work, so I had it redo the comparison before accepting the "faster" claim. For the scheduling tests, the AI temporarily broke the code in three ways (reversed priority, no drop for a missing slot, no clear on rebuild) to confirm that the tests really fail when the logic is wrong.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I wrote 41 pytest tests (`tests/test_pawpal.py`), and they all pass. They cover:
- **Basic behavior:** marking a task complete changes its status, and adding a task increases the pet's task count.
- **Sorting and filtering:** tasks come back in time order, equal times fall back to creation order, the input list isn't modified, and filters work by pet, by status and by both.
- **Recurring tasks:** completing a daily task creates a copy due today + 1 day, and a weekly task one due today + 7 days. A one-time task creates nothing, completing twice never duplicates, a task completed late is dated from today, and finishing a future copy early doesn't create two copies for the same day.
- **Conflict detection:** warnings for the same time on different pets and for an overlap on the same pet, and no warning for back-to-back or completed tasks.
- **The plan (`build_plan`):**
  - non-overlapping tasks are kept
  - the higher-priority task keeps its slot and the lower one moves later
  - equal-priority ties go to the earlier time, then creation order
  - a task moves past a chain of blocking tasks
  - a task is dropped when no slot is left or when it is outside the window
  - completed and other-day tasks are left out
  - every entry has a reason and the plan is sorted by time
  - rebuilding twice doesn't duplicate entries, and it plans across several pets
- **Edit and remove:** valid edits change only the given fields, and bad edits (a field that can't be edited, an invalid value, an unknown id) raise an error and leave the task unchanged. Removing a task works and an unknown id is rejected. An edit or removal also changes the regenerated plan.
- **Window, boundaries and validation:** `set_window` updates the window and rejects a bad one, and changing it changes the plan. Tasks that exactly fit or run one minute over are handled, empty owners and pets give empty results, and bad input (zero duration, a task past midnight, an inverted window, a duplicate pet name) is rejected.

These matter because the scheduler's value is that its decisions are right and explainable. A silent mistake, like the wrong task winning a conflict or a task landing outside the owner's window, would make the plan untrustworthy. As a check, I also temporarily broke the code three ways (reversed priority, no drop for a missing slot, no clear on rebuild), and the tests failed each time, so they do detect real mistakes.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident, about 4 out of 5, in the core scheduling rules: priority ordering, tie-breaks, moving and dropping, the window limit, sorting, filtering and recurring tasks each have a test that fails when the logic is broken. Some gaps remain:
- The Streamlit app was verified by running it, and earlier through Streamlit's test runner in throwaway scripts, but it has no automated tests in the suite. The newest UI changes, the filters and the custom species box, were only checked by running the app.
- `build_plan` places tasks greedily by priority, so it can drop a task that a smarter arrangement would have kept. The tests confirm the rule is applied consistently, not that the result is optimal.
- Blank task names are accepted, and a plan that crosses midnight is untested.

With more time I would test:
- **Many conflicts:** several tasks stacked on the same time, and a moved task that is pushed past the window end by a chain.
- **Dates:** a recurring task completed on the last day of a month or year, and the plan when "today" changes while the app is open.
- **Edits that cause problems:** editing a task so it now overlaps another, or changing a task's time after it has already been planned.
- **Ties across pets:** two pets with identical tasks at the same time.
- **The UI:** automated tests for adding a pet with a custom species, filtering, and generating a schedule.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied that the scheduler explains itself. Every task in the plan is kept, moved or dropped, with a one-sentence reason like "moved from 12:30 to 12:45 because it overlapped Vet call". That came from the design decision to give each plan line its own `PlanEntry` with an outcome and reason, and it shows up in the UI, the demo script and the tests. I'm also happy that the logic stayed small and readable: a greedy priority rule is easy to predict, and the 41 tests, which I checked by deliberately breaking the code, make me trust it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would first replace the greedy placement with something that can rearrange tasks, for example trying to keep the most tasks possible, while still giving a one-sentence reason for each decision. I would also let tasks have flexible time windows instead of a fixed start time, and add owner preferences such as "no walks after 6pm". On the app side, I would add automated tests for the Streamlit UI, since it is currently only checked by hand, and I would reject blank task names. Finally, I'd keep the UML updated as I code instead of checking it once at the end.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Working with AI went best when I made the decisions and the AI did the drafting. The AI drafted quickly, but it also over-built (the `Plan` wrapper class), left wording ambiguous (what "logged first" means) and made claims I had to check (an unfair benchmark). Asking it for a judgment, such as "is this too complicated?", and then running everything myself, with the demo, the tests and the real app, caught real bugs like the Streamlit pet copy. For system design, I learned that tightening the requirements before writing any code saved the most work. Each rule I wrote down, like the tie-break order, became a clear test later.
