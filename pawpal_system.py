from __future__ import annotations
from dataclasses import dataclass
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
    parentTask: Optional[Task] = None
    subtasks: Optional[list[Task]] = None

    def addSubtask(self, task: Task) -> None:
        pass

    def createTask(self, title: str, desc: str, priority: Priority,
                   duration: int, day: str) -> None:
        pass

    def updateTask(self, field_name: str, value) -> None:
        pass

    def deleteTask(self) -> None:
        pass

    def setPriority(self, level: Priority) -> None:
        pass

    def setDuration(self, minutes: int) -> None:
        pass

    def setDay(self, day: str) -> None:
        pass


@dataclass
class Pet:
    petId: int
    ownerId: int
    name: str
    type: str
    age: Optional[int] = None
    breed: Optional[str] = None

    def enterInfo(self, name: str, type: str, age: int, breed: str) -> None:
        pass

    def displayInfo(self) -> str:
        pass

    def updateInfo(self, field_name: str, value) -> None:
        pass


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
        pass

    def displayInfo(self) -> str:
        pass

    def updateInfo(self, field_name: str, value) -> None:
        pass


class DailySchedule:
    def __init__(self):
        self.scheduleId: int = None
        self.scheduleDate: date = None
        self.tasks: list[Task] = []
        self.startTime: Optional[time] = None
        self.endTime: Optional[time] = None

    def generateSchedule(self, tasks: list[Task]) -> None:
        pass

    def addTask(self, task: Task) -> None:
        pass

    def removeTask(self, taskId: int) -> None:
        pass

    def checkOffTask(self, taskId: int) -> None:
        pass

    def displaySchedule(self) -> str:
        pass

    def getTotalDuration(self) -> int:
        pass
