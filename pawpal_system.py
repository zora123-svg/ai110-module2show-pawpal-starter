from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

# Priority → sort weight (lower = scheduled first)
_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Task:
    taskId: int
    title: str
    dayOfWeek: str
    isCompleted: bool = False
    description: Optional[str] = None
    priority: Optional[Priority] = None
    duration: Optional[int] = None       # minutes
    petId: Optional[int] = None
    parentTask: Optional[Task] = None
    subtasks: list[Task] = field(default_factory=list)
    startTime: Optional[time] = None     # assigned by DailySchedule.assignTimeSlots
    recurrenceDays: list[str] = field(default_factory=list)  # e.g. ["Monday","Wednesday","Friday"]
    recurrence: Optional[str] = None     # "daily" | "weekly" | None — controls auto-renewal
    due_date: Optional[date] = None      # stamped by assignTimeSlots; used by mark_task_complete

    def addSubtask(self, task: Task) -> None:
        """Attach a child task to this task and set its parent reference."""
        task.parentTask = self
        self.subtasks.append(task)

    def updateTask(self, field_name: str, value) -> None:
        """Set any field on this task by name, raising AttributeError if it doesn't exist."""
        if not hasattr(self, field_name):
            raise AttributeError(f"Task has no field '{field_name}'")
        setattr(self, field_name, value)

    def deleteTask(self) -> None:
        """Delete this task and all its subtasks, then detach from the parent."""
        # Cascades: clear all subtasks recursively, then detach from parent
        for subtask in list(self.subtasks):
            subtask.deleteTask()
        self.subtasks.clear()
        if self.parentTask and self in self.parentTask.subtasks:
            self.parentTask.subtasks.remove(self)
        self.parentTask = None

    def setPriority(self, level: Priority) -> None:
        """Assign a Priority level to this task."""
        self.priority = level

    def setDuration(self, minutes: int) -> None:
        """Set the estimated duration of this task in minutes."""
        self.duration = minutes

    def setDay(self, day: str) -> None:
        """Update the day of the week this task is scheduled for."""
        self.dayOfWeek = day

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.isCompleted = True

    def mark_task_complete(self, as_of: Optional[date] = None) -> Optional["Task"]:
        """Mark this task complete and return a cloned next-occurrence task if recurring.

        Parameters
        ----------
        as_of : date or None
            The reference date used for computing the next due date.
            Falls back to self.due_date, then date.today() when None.

        Returns
        -------
        Task or None
            A cloned Task with due_date set to the next scheduled date,
            or None if this task does not recur.
        """
        self.isCompleted = True

        # Resolve the reference date: explicit arg > stamped due_date > today
        reference = as_of or self.due_date or date.today()

        if self.recurrence == "daily":
            # Next occurrence is exactly one day after the reference date
            next_due = reference + timedelta(days=1)
        elif self.recurrence == "weekly":
            # Next occurrence is exactly seven days (one week) after the reference date
            next_due = reference + timedelta(weeks=1)
        else:
            return None  # Non-recurring task — nothing to queue

        clone = self.next_occurrence(reference)
        if clone is not None:
            clone.due_date = next_due
        return clone

    def next_occurrence(self, from_date: date) -> Optional[Task]:
        """Return a new Task representing the next recurrence of this task.

        The clone is identical to this task except:
        - isCompleted is reset to False
        - startTime is cleared (will be reassigned by assignTimeSlots)
        - dayOfWeek reflects the next occurrence date
        - taskId is offset by 10_000 to avoid collisions (use a real ID
          generator in production)

        Returns None when recurrence is not set.
        """
        if self.recurrence == "daily":
            next_date = from_date + timedelta(days=1)
        elif self.recurrence == "weekly":
            next_date = from_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            taskId=self.taskId + 10_000,
            title=self.title,
            dayOfWeek=next_date.strftime("%A"),
            description=self.description,
            priority=self.priority,
            duration=self.duration,
            petId=self.petId,
            recurrence=self.recurrence,
            recurrenceDays=list(self.recurrenceDays),
        )


@dataclass
class Pet:
    petId: int
    ownerId: int
    name: str
    type: str
    age: Optional[int] = None
    breed: Optional[str] = None
    tasks: list[Task] = field(default_factory=list)

    def enterInfo(self, name: str, type: str, age: int, breed: str) -> None:
        """Bulk-set all profile fields for this pet."""
        self.name = name
        self.type = type
        self.age = age
        self.breed = breed

    def displayInfo(self) -> str:
        """Return a formatted one-line summary of this pet's profile."""
        breed_str = f", {self.breed}" if self.breed else ""
        age_str = f", age {self.age}" if self.age is not None else ""
        return f"{self.name} ({self.type}{breed_str}{age_str})"

    def updateInfo(self, field_name: str, value) -> None:
        """Set any profile field on this pet by name, raising AttributeError if it doesn't exist."""
        if not hasattr(self, field_name):
            raise AttributeError(f"Pet has no field '{field_name}'")
        setattr(self, field_name, value)

    def addTask(self, task: Task) -> None:
        """Append a task to this pet's list and stamp it with this pet's ID."""
        task.petId = self.petId
        self.tasks.append(task)

    def removeTask(self, taskId: int) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.taskId != taskId]


# ---------------------------------------------------------------------------
# Regular classes
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self):
        self.ownerId: int = None
        self.name: str = None
        self.age: int = None
        self.dateOfBirth: date = None
        self.email: str = None
        self.phoneNumber: str = None
        self.pets: list[Pet] = []
        self.schedules: list[DailySchedule] = []

    def enterInfo(self, name: str, age: int, dob: date,
                  email: str, phone: str) -> None:
        """Bulk-set all profile fields for this owner."""
        self.name = name
        self.age = age
        self.dateOfBirth = dob
        self.email = email
        self.phoneNumber = phone

    def displayInfo(self) -> str:
        """Return a formatted multi-line summary of this owner and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "none"
        return (
            f"Owner: {self.name} (age {self.age})\n"
            f"  Email: {self.email} | Phone: {self.phoneNumber}\n"
            f"  Pets: {pet_names}"
        )

    def updateInfo(self, field_name: str, value) -> None:
        """Set any profile field on this owner by name, raising AttributeError if it doesn't exist."""
        if not hasattr(self, field_name):
            raise AttributeError(f"Owner has no field '{field_name}'")
        setattr(self, field_name, value)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster and sync its ownerId."""
        pet.ownerId = self.ownerId
        self.pets.append(pet)

    def removePet(self, petId: int) -> None:
        """Remove the pet with the given ID from this owner's roster."""
        self.pets = [p for p in self.pets if p.petId != petId]

    def getAllTasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class DailySchedule:
    MAX_DAILY_MINUTES = 120  # soft cap for a manageable day

    def __init__(self):
        self.scheduleId: int = None
        self.ownerId: int = None
        self.scheduleDate: date = None
        self.tasks: dict[int, Task] = {}       # {taskId: Task}
        self.startTime: Optional[time] = None
        self.endTime: Optional[time] = None
        self._pet_names: dict[int, str] = {}   # {petId: pet.name} — built by loadFromOwner
        self._pending_next: list[Task] = []    # next-occurrence tasks queued by checkOffTask

    @staticmethod
    def _task_matches_day(task: Task, day_name: str) -> bool:
        """Return True if the task should appear on the given day of the week.

        Recurrence lookup order
        -----------------------
        1. If ``task.recurrenceDays`` is non-empty, check whether ``day_name``
           appears in that list (case-insensitive).  This supports tasks that
           repeat on multiple specific days, e.g. a walk on Mon/Wed/Fri.
        2. Otherwise fall back to ``task.dayOfWeek`` for a simple single-day
           match — the original scheduling behaviour.

        Parameters
        ----------
        task : Task
            The task to evaluate.
        day_name : str
            Full English day name as returned by ``date.strftime("%A")``,
            e.g. ``"Tuesday"``.

        Returns
        -------
        bool
            True when the task is eligible for ``day_name``.
        """
        if task.recurrenceDays:
            return day_name.lower() in [d.lower() for d in task.recurrenceDays]
        return task.dayOfWeek.lower() == day_name.lower()

    def generateSchedule(self, tasks: list[Task]) -> None:
        """Populate the schedule from a flat task list using day-filtering and priority sorting.

        Algorithm
        ---------
        1. Filter: keep only tasks whose day matches ``scheduleDate`` via
           ``_task_matches_day`` (respects both single-day and recurrenceDays).
           When ``scheduleDate`` is None every task passes the filter.
        2. Sort: order the matched tasks by priority weight
           (HIGH=0, MEDIUM=1, LOW=2, unset=99) so that the highest-priority
           tasks receive the earliest time slots when ``assignTimeSlots`` runs.
        3. Store: insert tasks into ``self.tasks`` dict in sorted order;
           dict insertion order (Python 3.7+) preserves the sort for iteration.

        Parameters
        ----------
        tasks : list[Task]
            Flat list of all candidate tasks, typically from
            ``Owner.getAllTasks()``.
        """
        self.tasks.clear()
        day_name = self.scheduleDate.strftime("%A") if self.scheduleDate else None

        matching = [t for t in tasks if day_name is None or self._task_matches_day(t, day_name)]
        matching.sort(key=lambda t: _PRIORITY_ORDER.get(t.priority, 99))

        for task in matching:
            self.tasks[task.taskId] = task

    def loadFromOwner(self, owner: Owner) -> None:
        """Convenience: pull all tasks from every pet the owner has, then generate."""
        self.ownerId = owner.ownerId
        self._pet_names = {pet.petId: pet.name for pet in owner.pets}
        self.generateSchedule(owner.getAllTasks())

    def addTask(self, task: Task) -> None:
        """Insert a single task into this schedule, keyed by its ID."""
        self.tasks[task.taskId] = task

    def removeTask(self, taskId: int) -> None:
        """Remove the task with the given ID from this schedule, if present."""
        self.tasks.pop(taskId, None)

    def checkOffTask(self, taskId: int) -> None:
        """Mark a task complete and, if it recurs, queue the next occurrence.

        For "daily" tasks the next instance is scheduled for tomorrow.
        For "weekly" tasks it is scheduled for the same day next week.
        The queued task is stored in _pending_next; retrieve it with
        get_pending_next().
        """
        if taskId not in self.tasks:
            return
        task = self.tasks[taskId]
        # mark_task_complete handles isCompleted=True + recurrence clone + due_date stamping
        next_task = task.mark_task_complete(self.scheduleDate or date.today())
        if next_task:
            self._pending_next.append(next_task)

    def get_pending_next(self) -> list[Task]:
        """Return all next-occurrence tasks queued since the last call.

        Clears the queue so repeated calls do not return duplicates.
        """
        queued = list(self._pending_next)
        self._pending_next.clear()
        return queued

    def assignTimeSlots(self, start: time) -> None:
        """Assign sequential, non-overlapping start times to every task in the schedule.

        Algorithm
        ---------
        A cursor ``datetime`` is initialised to ``(scheduleDate, start)``.
        For each task (in current dict order, which is priority-sorted after
        ``generateSchedule``):

        - ``task.startTime``  is set to the cursor's time component.
        - ``task.due_date``   is stamped with ``scheduleDate`` so that
          ``mark_task_complete`` can calculate the next recurrence without
          needing an external date argument.
        - The cursor advances by ``task.duration`` minutes before the next task.

        Tasks with no duration contribute 0 minutes to the cursor, so they
        share a start time with the following task.  Call this method after
        ``generateSchedule`` (and after any manual ``addTask`` calls) to ensure
        all tasks reflect the final insertion order.

        Parameters
        ----------
        start : time
            Wall-clock start time for the first task, e.g. ``time(8, 0)``.
        """
        ref_date = self.scheduleDate or date.today()
        cursor = datetime.combine(ref_date, start)
        for task in self.tasks.values():
            task.startTime = cursor.time()
            task.due_date = ref_date   # stamp the schedule date as this task's due date
            cursor += timedelta(minutes=task.duration or 0)

    def filterByPet(self, petId: int) -> list[Task]:
        """Return all scheduled tasks belonging to the given pet."""
        return [t for t in self.tasks.values() if t.petId == petId]

    def filterByStatus(self, completed: bool) -> list[Task]:
        """Return scheduled tasks whose isCompleted matches the given flag."""
        return [t for t in self.tasks.values() if t.isCompleted == completed]

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks that match all supplied filters (AND logic).

        Parameters
        ----------
        completed : bool or None
            - True  → only completed tasks
            - False → only pending tasks
            - None  → completion status is not filtered
        pet_name : str or None
            Case-insensitive pet name to match against.
            None means all pets are included.

        Both filters are applied together when both are provided.
        Omitting a filter (leaving it as None) means "no restriction on that axis".

        Examples
        --------
        filter_tasks()                         # all tasks
        filter_tasks(completed=False)          # all pending tasks
        filter_tasks(pet_name="Buddy")         # all of Buddy's tasks
        filter_tasks(completed=True, pet_name="Buddy")  # Buddy's done tasks only
        """
        results = list(self.tasks.values())

        if completed is not None:
            results = [t for t in results if t.isCompleted == completed]

        if pet_name is not None:
            target = pet_name.lower()
            results = [
                t for t in results
                if self._pet_names.get(t.petId, "").lower() == target
            ]

        return results

    def sort_by_time(self) -> list[Task]:
        """Return all scheduled tasks sorted by startTime (earliest first).

        The lambda converts each task's startTime to an "HH:MM" string before
        comparing.  Lexicographic order on zero-padded "HH:MM" strings is
        identical to chronological order, so sorted() needs no extra logic.

        Tasks whose startTime is None are placed at the end by defaulting to
        the sentinel string "99:99", which sorts after any valid time.

        Example
        -------
        sorted(..., key=lambda t: t.startTime.strftime("%H:%M") if t.startTime else "99:99")

        "08:00" < "08:30" < "09:15"  — works because Python compares strings
        character-by-character left-to-right, so the hour digits are evaluated
        first, then the minute digits.
        """
        return sorted(
            self.tasks.values(),
            key=lambda t: t.startTime.strftime("%H:%M") if t.startTime else "99:99",
        )

    def detectConflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap.

        Only considers tasks that have both startTime and duration set.
        Strategy: sort by startTime, then for each task A scan forward only
        while the next task's start falls inside A's window.  This is O(n²)
        worst-case but exits the inner loop early — fine for daily task counts
        and guaranteed not to raise on missing/None fields.
        """
        timed = [t for t in self.tasks.values() if t.startTime and t.duration]
        timed.sort(key=lambda t: t.startTime)
        conflicts: list[tuple[Task, Task]] = []
        ref_date = self.scheduleDate or date.today()
        for i, a in enumerate(timed):
            a_start = datetime.combine(ref_date, a.startTime)
            a_end   = a_start + timedelta(minutes=a.duration)
            for b in timed[i + 1:]:
                b_start = datetime.combine(ref_date, b.startTime)
                if b_start >= a_end:
                    break  # sorted by start — no further overlaps possible with A
                conflicts.append((a, b))
        return conflicts

    def get_conflict_warnings(self) -> list[str]:
        """Return a warning string for every overlapping task pair.

        Lightweight wrapper around detectConflicts() that formats each conflict
        as a human-readable WARNING line.  Always returns a list — never raises
        and never crashes the caller even when the schedule is empty or tasks
        lack time information.

        Readability note: the repeated end-time calculation is extracted into
        _fmt_slot() so each call site reads like plain English.  A pure list
        comprehension with an inline lambda was considered (more 'Pythonic')
        but rejected here because the format string is complex enough that
        splitting it across named variables makes future edits safer.

        Example output line:
          WARNING: 'Morning Walk' (Buddy, 08:00-08:30) overlaps with
                   'Vet Check-up' (Buddy, 08:15-08:45)
        """
        ref_date = self.scheduleDate or date.today()

        def _fmt_slot(task: Task) -> str:
            """'Title' (PetName, HH:MM-HH:MM)"""
            end = (datetime.combine(ref_date, task.startTime)
                   + timedelta(minutes=task.duration)).time()
            pet = self._pet_names.get(task.petId, f"pet#{task.petId}")
            return (f"'{task.title}' ({pet}, "
                    f"{task.startTime.strftime('%H:%M')}-{end.strftime('%H:%M')})")

        warnings: list[str] = []
        for a, b in self.detectConflicts():
            warnings.append(f"WARNING: {_fmt_slot(a)} overlaps with {_fmt_slot(b)}")
        return warnings

    def displaySchedule(self) -> str:
        """Return a formatted, column-aligned view of all tasks for the scheduled day.

        Tasks are shown sorted by startTime when available, else in priority order.
        """
        if not self.tasks:
            return f"Schedule for {self.scheduleDate}: no tasks."
        lines = [f"Schedule for {self.scheduleDate}:"]
        ordered = sorted(
            self.tasks.values(),
            key=lambda t: t.startTime or time(23, 59),
        )
        ref_date = self.scheduleDate or date.today()
        for task in ordered:
            status   = "  [x]" if task.isCompleted else "  [ ]"
            priority = f"[{task.priority.value:<6}]" if task.priority else "[      ]"
            title    = task.title[:28].ljust(28)
            duration = f"{task.duration:>3} min" if task.duration is not None else "  —    "
            if task.startTime and task.duration:
                start_dt = datetime.combine(ref_date, task.startTime)
                end_dt   = start_dt + timedelta(minutes=task.duration)
                slot = f"  {task.startTime.strftime('%H:%M')}-{end_dt.time().strftime('%H:%M')}"
            else:
                slot = ""
            lines.append(f"{status}  {priority}  {title}  {duration}{slot}")
        return "\n".join(lines)

    def getTotalDuration(self) -> int:
        """Return the sum of all task durations in minutes, skipping tasks with no duration set."""
        return sum(t.duration for t in self.tasks.values() if t.duration is not None)
