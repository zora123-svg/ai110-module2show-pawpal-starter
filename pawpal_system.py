from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


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
    duration: Optional[int] = None  # minutes
    petId: Optional[int] = None
    parentTask: Optional[Task] = None
    subtasks: list[Task] = field(default_factory=list)

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
        self.tasks: dict[int, Task] = {}  # {taskId: Task}
        self.startTime: Optional[time] = None
        self.endTime: Optional[time] = None

    def generateSchedule(self, tasks: list[Task]) -> None:
        """Populate this schedule from a flat list of tasks, filtered to scheduleDate's day."""
        self.tasks.clear()
        day_name = self.scheduleDate.strftime("%A") if self.scheduleDate else None
        for task in tasks:
            if day_name is None or task.dayOfWeek.lower() == day_name.lower():
                self.tasks[task.taskId] = task

    def loadFromOwner(self, owner: Owner) -> None:
        """Convenience: pull all tasks from every pet the owner has, then generate."""
        self.ownerId = owner.ownerId
        self.generateSchedule(owner.getAllTasks())

    def addTask(self, task: Task) -> None:
        """Insert a single task into this schedule, keyed by its ID."""
        self.tasks[task.taskId] = task

    def removeTask(self, taskId: int) -> None:
        """Remove the task with the given ID from this schedule, if present."""
        self.tasks.pop(taskId, None)

    def checkOffTask(self, taskId: int) -> None:
        """Mark the task with the given ID as completed within this schedule."""
        if taskId in self.tasks:
            self.tasks[taskId].isCompleted = True

    def displaySchedule(self) -> str:
        """Return a formatted, column-aligned view of all tasks for the scheduled day."""
        if not self.tasks:
            return f"Schedule for {self.scheduleDate}: no tasks."
        lines = [f"Schedule for {self.scheduleDate}:"]
        for task in self.tasks.values():
            status   = "  ✓" if task.isCompleted else "  •"
            priority = f"[{task.priority.value:<6}]" if task.priority else "[      ]"
            title    = task.title[:28].ljust(28)
            duration = f"{task.duration:>3} min" if task.duration is not None else "  —    "
            lines.append(f"{status}  {priority}  {title}  {duration}")
        return "\n".join(lines)

    def getTotalDuration(self) -> int:
        """Return the sum of all task durations in minutes, skipping tasks with no duration set."""
        # Skips tasks where duration is None
        return sum(t.duration for t in self.tasks.values() if t.duration is not None)
