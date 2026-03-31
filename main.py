from datetime import date
from pawpal_system import Task, Pet, Owner, DailySchedule, Priority

# ---------------------------------------------------------------------------
# 1. Create Owner
# ---------------------------------------------------------------------------
owner = Owner()
owner.ownerId = 1
owner.enterInfo(
    name="Jordan",
    age=30,
    dob=date(1996, 4, 15),
    email="jordan@example.com",
    phone="555-0100",
)

# ---------------------------------------------------------------------------
# 2. Create Pets
# ---------------------------------------------------------------------------
buddy = Pet(petId=1, ownerId=owner.ownerId, name="Buddy", type="Dog", age=3, breed="Labrador")
whiskers = Pet(petId=2, ownerId=owner.ownerId, name="Whiskers", type="Cat", age=5, breed="Siamese")

owner.addPet(buddy)
owner.addPet(whiskers)

# ---------------------------------------------------------------------------
# 3. Add Tasks  (dayOfWeek matches today: Tuesday, 2026-03-31)
# ---------------------------------------------------------------------------

# Buddy's tasks
morning_walk = Task(taskId=101, title="Morning Walk", dayOfWeek="Tuesday", duration=30)
morning_walk.setPriority(Priority.HIGH)
morning_walk.description = "Walk around the block before breakfast"
buddy.addTask(morning_walk)

feeding_buddy = Task(taskId=102, title="Feed Buddy", dayOfWeek="Tuesday", duration=10)
feeding_buddy.setPriority(Priority.HIGH)
feeding_buddy.description = "One cup of dry kibble"
buddy.addTask(feeding_buddy)

# Whiskers' tasks
feeding_whiskers = Task(taskId=201, title="Feed Whiskers", dayOfWeek="Tuesday", duration=5)
feeding_whiskers.setPriority(Priority.MEDIUM)
feeding_whiskers.description = "Half a can of wet food"
whiskers.addTask(feeding_whiskers)

grooming = Task(taskId=202, title="Brush Whiskers", dayOfWeek="Tuesday", duration=15)
grooming.setPriority(Priority.LOW)
grooming.description = "Weekly coat brushing"
whiskers.addTask(grooming)

# ---------------------------------------------------------------------------
# 4. Build Today's Schedule and print it
# ---------------------------------------------------------------------------
schedule = DailySchedule()
schedule.scheduleId = 1
schedule.scheduleDate = date.today()   # 2026-03-31 (Tuesday)
schedule.loadFromOwner(owner)

WIDTH = 50

print("=" * WIDTH)
print("         PAWPAL+ — TODAY'S SCHEDULE".center(WIDTH))
print("=" * WIDTH)
print(f"  Owner : {owner.name}")
print(f"  Pets  :")
for pet in owner.pets:
    print(f"    - {pet.displayInfo()}")
print("-" * WIDTH)
print(schedule.displaySchedule())
print("-" * WIDTH)

used      = schedule.getTotalDuration()
cap       = DailySchedule.MAX_DAILY_MINUTES
remaining = cap - used
bar_fill  = min(used, cap)
bar_len   = 20
filled    = round(bar_fill / cap * bar_len)
bar       = "█" * filled + "░" * (bar_len - filled)

print(f"  Time used    : {used} min  [{bar}]  cap {cap} min")
if remaining >= 0:
    print(f"  Time left    : {remaining} min")
else:
    print(f"  Over cap by  : {abs(remaining)} min  ⚠")
print("=" * WIDTH)
