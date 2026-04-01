# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
Four classes were identified for this system, each with a distinct responsibility.

Owner captures and manages the personal information of the app user — name, age, date of birth, email, and phone number. It also holds references to the owner's pets and schedules.

Pet handles animal-specific information such as name, type, breed, and age. It maintains a link back to its owner via ownerId and follows the same enter, display, and update pattern as Owner.

Task represents a single to-do item. It tracks the title, assigned day, duration, priority, and completion status. It also supports a parent-child hierarchy so tasks can be broken into subtasks, and covers full CRUD operations.

DailySchedule takes a list of tasks and organizes them into a schedule for a specific date. It handles generating, adding, and removing tasks, marking tasks as complete, and calculating the total duration for the day.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes I added petId to Task and ownerID to daily schedule because those were missing relationships. I also changed the data type in checkOffTask(taskID) into a dictionary so that we have a faster look up time. I removed the redundant createtask because the construction in our dataclass handles it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints: task priority (HIGH/MEDIUM/LOW), a daily time budget, and day-of-week filtering for recurring tasks. Priority is the backbone — tasks are sorted most to least urgent before any time slots are assigned, so feeding and walking always land before optional grooming, just like a real owner would plan their morning. The time budget acts more like a warning flag than a hard limit; if the day looks overloaded, the progress bar surfaces that, but the scheduler won't silently drop tasks — a skipped feeding is a real problem, so the owner decides what gets cut. Day filtering just keeps things clean by hiding tasks that aren't due today rather than deferring them. Priority was treated as the most important constraint because it directly reflects what the owner cares about, while the other two are guardrails that keep the schedule realistic.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The tradeoff in `detectConflicts()` was simplicity over theoretical efficiency — it uses a nested loop (O(n²) worst-case) rather than a sweep-line algorithm, because a pet owner typically has 5–20 tasks a day where the difference is microseconds and the simpler code is easier to read and verify at a glance. For `get_conflict_warnings()`, the tradeoff was readability over brevity — a single list comprehension with an inline lambda was considered but rejected because the format string is complex enough that burying it in a lambda makes future edits risky. Instead, a named inner function `_fmt_slot()` was pulled out, removing the duplicated end-time calculation and keeping each line readable on its own. Two extra lines felt like a fair trade for something any contributor can update without mentally untangling a compound expression.

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
