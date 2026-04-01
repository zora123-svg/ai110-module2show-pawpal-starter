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

## Smarter Scheduling

The core scheduling logic lives in `pawpal_system.py` and was extended beyond the original skeleton with four algorithmic features.

### Priority-based task ordering
`DailySchedule.generateSchedule` filters tasks to the current day of the week and immediately sorts them HIGH → MEDIUM → LOW before assigning time slots.  This guarantees that a pet's feeding and walk always appear earlier in the day than optional grooming, matching how a real owner would plan their morning.

### Recurring tasks
`Task` carries two recurrence fields:

| Field | Purpose |
|---|---|
| `recurrenceDays` | List of day names the task appears on (e.g. `["Monday","Wednesday","Friday"]`).  Overrides `dayOfWeek` during filtering. |
| `recurrence` | `"daily"` or `"weekly"` — controls automatic renewal when the task is completed. |

When `checkOffTask` marks a task complete, it calls `Task.mark_task_complete`, which uses Python's `timedelta` to calculate the next due date (`+1 day` or `+1 week`) and returns a ready-to-use clone.  The clone is queued in `DailySchedule._pending_next` and retrieved with `get_pending_next()`.

### Sorting and filtering
| Method | What it does |
|---|---|
| `sort_by_time()` | Returns tasks ordered by `startTime` using a `sorted()` lambda on `"HH:MM"` strings. |
| `filter_tasks(completed, pet_name)` | AND-logic filter on completion status and/or pet name (case-insensitive). |
| `filterByPet(petId)` | Returns tasks for one specific pet. |
| `filterByStatus(completed)` | Returns only done or only pending tasks. |

### Conflict detection
`detectConflicts()` sorts tasks by `startTime` and uses an early-exit nested scan to find every pair of overlapping time windows — across the same pet or different pets.  `get_conflict_warnings()` wraps the raw pairs into human-readable `WARNING:` strings and always returns a list, so the caller never needs to handle an exception.

```
WARNING: 'Morning Walk' (Buddy, 08:00-08:30) overlaps with 'Vet Check-up' (Buddy, 08:15-08:45)
```

---

## Testing PawPal+

Tests live in `tests/test_pawpal.py` and cover the five most critical scheduling behaviors.

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### What is tested

The tests cover five core behaviors. Checking off a task should mark it done and keep it that way — the first test makes sure it doesn't quietly reset. The second confirms that tasks added to a pet are actually saved and not silently dropped. From there, the focus shifts to scheduling: one test verifies that the daily view shows tasks in the order they happen rather than the order they were entered, and another checks that finishing a recurring task automatically queues a fresh copy for the next day so nothing slips through. Finally, there's a conflict test — if two tasks overlap, the app should catch it before it becomes the owner's problem.

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
