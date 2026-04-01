from datetime import date, time
from pawpal_system import Task, Pet, Priority, DailySchedule


# ---------------------------------------------------------------------------
# Test 1 — Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip isCompleted from False to True."""
    task = Task(taskId=1, title="Morning Walk", dayOfWeek="Monday")

    assert task.isCompleted is False  # starts incomplete

    task.mark_complete()

    assert task.isCompleted is True   # now complete


# ---------------------------------------------------------------------------
# Test 2 — Task Addition
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(petId=1, ownerId=1, name="Buddy", type="Dog")

    assert len(pet.tasks) == 0  # starts with no tasks

    task = Task(taskId=101, title="Feed Buddy", dayOfWeek="Monday")
    pet.addTask(task)

    assert len(pet.tasks) == 1  # one task added


# ---------------------------------------------------------------------------
# Test 3 — Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks should come back earliest startTime first after sort_by_time()."""
    # Mike has three tasks manually assigned out-of-order times
    walk  = Task(taskId=1, title="Morning Walk",  dayOfWeek="Tuesday", duration=30)
    feed  = Task(taskId=2, title="Breakfast Feed", dayOfWeek="Tuesday", duration=15)
    groom = Task(taskId=3, title="Grooming",       dayOfWeek="Tuesday", duration=60)

    walk.startTime  = time(9, 0)   # latest
    feed.startTime  = time(7, 30)  # earliest
    groom.startTime = time(8, 0)   # middle

    schedule = DailySchedule()
    schedule.scheduleDate = date(2026, 4, 1)
    for t in [walk, feed, groom]:
        schedule.addTask(t)

    ordered = schedule.sort_by_time()

    assert [t.taskId for t in ordered] == [2, 3, 1]  # feed → groom → walk


# ---------------------------------------------------------------------------
# Test 4 — Recurrence Logic
# ---------------------------------------------------------------------------

def test_daily_recurrence_creates_next_day_task():
    """Marking a daily task complete should return a clone due the following day."""
    # Mike completes Buddy's daily walk on Wednesday April 1
    walk = Task(
        taskId=1,
        title="Morning Walk",
        dayOfWeek="Wednesday",
        recurrence="daily",
        duration=30,
    )

    schedule = DailySchedule()
    schedule.scheduleDate = date(2026, 4, 1)
    schedule.addTask(walk)
    schedule.assignTimeSlots(time(8, 0))

    schedule.checkOffTask(1)
    next_tasks = schedule.get_pending_next()

    assert len(next_tasks) == 1                              # exactly one clone
    assert next_tasks[0].due_date == date(2026, 4, 2)        # due tomorrow
    assert next_tasks[0].dayOfWeek == "Thursday"             # correct day name
    assert next_tasks[0].isCompleted is False                # reset to incomplete


# ---------------------------------------------------------------------------
# Test 5 — Conflict Detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks sharing the same start time should appear in detectConflicts()."""
    # Mike books Buddy's grooming and Luna's vet visit both at 09:00
    groom = Task(taskId=1, title="Grooming",   dayOfWeek="Tuesday", duration=60)
    vet   = Task(taskId=2, title="Vet Visit",  dayOfWeek="Tuesday", duration=30)

    groom.startTime = time(9, 0)
    vet.startTime   = time(9, 0)

    schedule = DailySchedule()
    schedule.scheduleDate = date(2026, 4, 1)
    schedule.addTask(groom)
    schedule.addTask(vet)

    conflicts = schedule.detectConflicts()

    assert len(conflicts) == 1                  # one overlapping pair found
    ids = {t.taskId for pair in conflicts for t in pair}
    assert ids == {1, 2}                        # both tasks are in the conflict
