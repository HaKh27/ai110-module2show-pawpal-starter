# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

1. User should be able to label activities by priority (Levels: Low, Medium, High)
2. User should be able to schedule activities while making sure there's no conflict and have some sort of conflict resolution 
3. User should be able to create a Pet object 

1. Priority class attribute: priority level , function: classify an activity's priority 
2. Schedule a task attribute: task name, task time   function: check for collisons, check if task is valid in that time slot 
3. Pet object attribute: pet name   function: add pet to family 
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
yes, 
1. I wanted to make priority a class, but it makes more sense for there to be a TASK class with priority as an attribute.  A user can assign each task a priority of Low, Medium or High (default: Medium). The scheduler places higher-priority tasks first. When the day can't fit everything, lower-priority tasks are dropped first, and the plan lists each dropped task with the reason. Ties within the same priority go to the task with the earlier scheduled time. If the times are also equal, the task that was logged first goes first.
Responsibilities
- Task holds the priority attribute.
- Scheduler sorts by it.

2. A user can add tasks with a name, a fixed start time, a duration and a priority. End time is computed as start time plus duration. The scheduler detects when two tasks overlap in time. When there's a conflict, the higher-priority task keeps its slot. The lower-priority task is moved to the next free slot later in the day, or dropped if there isn't one, and the plan explains either outcome. A task must fit entirely inside the owner's available window. A task that starts before the window, or can't fit before it closes, is dropped with the reason "outside available window". A task that starts inside the window but overlaps a higher-priority task is moved or dropped as described above. Equal-priority conflicts use the same tie-break as item 1.
Responsibilities
- Task holds name, start time, duration and priority.
- Scheduler detects overlaps, moves or drops tasks and records the reason for each.

3. A user can enter owner info (name and daily available window, a start and end time) and add one or more pets (name and species). Each task belongs to a pet. A user can add, edit or remove a task, and the plan regenerates from the updated list.
Responsibilities
- Owner holds name, available window and its pets, and has add_pet.
- Pet holds name, species and its tasks, and has add_task, edit_task and remove_task.

4. A user can view a generated daily plan, ordered by start time. Each entry shows the pet, task, start time, duration and priority. Beside it, the plan explains why each task was kept, moved or dropped. Dropped tasks are listed separately with their reason.
Responsibilities
- Scheduler builds the plan from all of the owner's pets' tasks and produces the explanation text.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
