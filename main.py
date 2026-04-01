from datetime import date, time
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
buddy    = Pet(petId=1, ownerId=owner.ownerId, name="Buddy",    type="Dog", age=3, breed="Labrador")
whiskers = Pet(petId=2, ownerId=owner.ownerId, name="Whiskers", type="Cat", age=5, breed="Siamese")

owner.addPet(buddy)
owner.addPet(whiskers)

# ---------------------------------------------------------------------------
# 3. Add Tasks
#
#    Recurring task: Buddy's morning walk repeats Mon / Wed / Fri / Tue / Thu
#    (recurrenceDays replaces the single dayOfWeek so it appears any weekday)
# ---------------------------------------------------------------------------

# Buddy — recurring walk (Mon–Fri), auto-renews daily
morning_walk = Task(taskId=101, title="Morning Walk", dayOfWeek="Monday", duration=30)
morning_walk.setPriority(Priority.HIGH)
morning_walk.description = "Walk around the block before breakfast"
morning_walk.recurrenceDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
morning_walk.recurrence = "daily"
buddy.addTask(morning_walk)

# Buddy — daily feeding, auto-renews daily
feeding_buddy = Task(taskId=102, title="Feed Buddy", dayOfWeek="Tuesday", duration=10)
feeding_buddy.setPriority(Priority.HIGH)
feeding_buddy.description = "One cup of dry kibble"
feeding_buddy.recurrence = "daily"
buddy.addTask(feeding_buddy)

# Whiskers — feeding, auto-renews daily
feeding_whiskers = Task(taskId=201, title="Feed Whiskers", dayOfWeek="Tuesday", duration=5)
feeding_whiskers.setPriority(Priority.MEDIUM)
feeding_whiskers.description = "Half a can of wet food"
feeding_whiskers.recurrence = "daily"
whiskers.addTask(feeding_whiskers)

# Whiskers — grooming, auto-renews weekly
grooming = Task(taskId=202, title="Brush Whiskers", dayOfWeek="Tuesday", duration=15)
grooming.setPriority(Priority.LOW)
grooming.description = "Weekly coat brushing"
grooming.recurrence = "weekly"
whiskers.addTask(grooming)

# ---------------------------------------------------------------------------
# 4. Build Today's Schedule
# ---------------------------------------------------------------------------
schedule = DailySchedule()
schedule.scheduleId  = 1
schedule.scheduleDate = date.today()
schedule.loadFromOwner(owner)   # filters by today + sorts HIGH → LOW

# Assign sequential time slots starting at 08:00
schedule.assignTimeSlots(time(8, 0))

WIDTH = 54

print("=" * WIDTH)
print("         PAWPAL+ - TODAY'S SCHEDULE".center(WIDTH))
print("=" * WIDTH)
print(f"  Owner : {owner.name}")
print(f"  Date  : {schedule.scheduleDate}  ({schedule.scheduleDate.strftime('%A')})")
print(f"  Pets  :")
for pet in owner.pets:
    print(f"    - {pet.displayInfo()}")
print("-" * WIDTH)
print(schedule.displaySchedule())
print("-" * WIDTH)

used      = schedule.getTotalDuration()
cap       = DailySchedule.MAX_DAILY_MINUTES
remaining = cap - used
bar_len   = 20
filled    = round(min(used, cap) / cap * bar_len)
bar       = "#" * filled + "-" * (bar_len - filled)

print(f"  Time used    : {used} min  [{bar}]  cap {cap} min")
if remaining >= 0:
    print(f"  Time left    : {remaining} min")
else:
    print(f"  Over cap by  : {abs(remaining)} min  (!)")
print("=" * WIDTH)

# ---------------------------------------------------------------------------
# 5. Conflict Detection
#    Inject two tasks that intentionally overlap to verify the detector.
#
#    Morning Walk runs 08:00-08:30.
#    Vet Check-up is manually stamped at 08:15 (duration 30 min → 08:15-08:45),
#    so it overlaps with Morning Walk by 15 minutes.
#    A second cross-pet collision: Whiskers' Nail Trim at 08:35 overlaps with
#    Feed Buddy (08:30-08:40) by 5 minutes.
# ---------------------------------------------------------------------------
from datetime import time as _time   # already imported at top; alias avoids shadowing

vet = Task(taskId=301, title="Vet Check-up", dayOfWeek=schedule.scheduleDate.strftime("%A"),
           duration=30, petId=buddy.petId)
vet.setPriority(Priority.HIGH)
vet.startTime = _time(8, 15)   # intentionally overlaps Morning Walk (08:00-08:30)
schedule.addTask(vet)

nail_trim = Task(taskId=302, title="Nail Trim", dayOfWeek=schedule.scheduleDate.strftime("%A"),
                 duration=20, petId=whiskers.petId)
nail_trim.setPriority(Priority.MEDIUM)
nail_trim.startTime = _time(8, 35)  # intentionally overlaps Feed Buddy (08:30-08:40)
schedule.addTask(nail_trim)

print("\n--- Schedule with injected conflicts ---")
print(schedule.displaySchedule())

print("\n--- Conflict Detection (get_conflict_warnings) ---")
warnings = schedule.get_conflict_warnings()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  [ok] No scheduling conflicts found.")

# Remove the conflicting tasks so the rest of the demo stays clean
schedule.removeTask(301)
schedule.removeTask(302)
print(f"\n  Conflict tasks removed. Tasks remaining: {len(schedule.tasks)}")

# ---------------------------------------------------------------------------
# 6. Filter by Pet
# ---------------------------------------------------------------------------
print("\n--- Filter: Buddy's Tasks ---")
for t in schedule.filterByPet(buddy.petId):
    slot = t.startTime.strftime("%H:%M") if t.startTime else "—"
    recur = f"  (recurs: {', '.join(t.recurrenceDays)})" if t.recurrenceDays else ""
    print(f"  [{slot}]  {t.title}{recur}")

print("\n--- Filter: Whiskers' Tasks ---")
for t in schedule.filterByPet(whiskers.petId):
    slot = t.startTime.strftime("%H:%M") if t.startTime else "—"
    print(f"  [{slot}]  {t.title}")

# ---------------------------------------------------------------------------
# 7. Complete tasks → auto-renewal queue
# ---------------------------------------------------------------------------
print("\n--- Completing all tasks ---")
next_tasks = {}   # tid -> next Task, collected here so we can print due_dates below
for tid in [101, 102, 201, 202]:
    schedule.checkOffTask(tid)
    t = schedule.tasks[tid]
    tag = f"[{t.recurrence}]" if t.recurrence else "[one-time]"
    due_str = str(t.due_date) if t.due_date else "n/a"
    print(f"  checked off: {t.title:<28} {tag}  due={due_str}")

# collect the queued next-occurrences now so we can show their due_dates
pending_next = schedule.get_pending_next()
next_by_base = {nxt.taskId - 10_000: nxt for nxt in pending_next}

print("\n  due_date timedelta summary:")
for tid in [101, 102, 201, 202]:
    t = schedule.tasks[tid]
    nxt = next_by_base.get(tid)
    if nxt:
        recur_label = f"+1 day " if t.recurrence == "daily" else "+1 week"
        print(f"    {t.title:<28}  due={t.due_date}  {recur_label}  next_due={nxt.due_date}")
    else:
        print(f"    {t.title:<28}  due={t.due_date}  [one-time, no next]")

print("\n--- Auto-renewed next occurrences (get_pending_next) ---")
# queue was already drained above; re-use the saved list
for nxt in pending_next:
    print(f"  taskId={nxt.taskId}  '{nxt.title}'  -> {nxt.dayOfWeek}"
          f"  [{nxt.recurrence}]  next_due={nxt.due_date}")

print("\n--- get_pending_next() is now empty (queue cleared) ---")
print(f"  {schedule.get_pending_next()}")

print("\n--- Filter: Completed Tasks ---")
done = schedule.filterByStatus(completed=True)
print(f"  {len(done)} task(s) done: {[t.title for t in done]}")

print("\n--- Filter: Pending Tasks ---")
pending = schedule.filterByStatus(completed=False)
print(f"  {len(pending)} task(s) pending: {[t.title for t in pending]}")


# ---------------------------------------------------------------------------
# 8. filter_tasks() — combined completion-status / pet-name filter
# ---------------------------------------------------------------------------
def _show_filter(label: str, tasks: list) -> None:
    names = [t.title for t in tasks] if tasks else ["(none)"]
    print(f"  {label}: {names}")

print("--- filter_tasks() ---")
_show_filter("all tasks                       ", schedule.filter_tasks())
_show_filter("completed=True                  ", schedule.filter_tasks(completed=True))
_show_filter("completed=False                 ", schedule.filter_tasks(completed=False))
_show_filter("pet_name='Buddy'                ", schedule.filter_tasks(pet_name="Buddy"))
_show_filter("pet_name='Whiskers'             ", schedule.filter_tasks(pet_name="Whiskers"))
_show_filter("pet_name='buddy' (case-insens.) ", schedule.filter_tasks(pet_name="buddy"))
_show_filter("completed=True, pet_name='Buddy'", schedule.filter_tasks(completed=True,  pet_name="Buddy"))
_show_filter("completed=False,pet_name='Buddy'", schedule.filter_tasks(completed=False, pet_name="Buddy"))
print()

# ---------------------------------------------------------------------------
# 9. sort_by_time()  — explicit demo of the lambda/sorted approach
# ---------------------------------------------------------------------------
print("--- sort_by_time() ---")
print("  Lambda key: t.startTime.strftime('%H:%M') if t.startTime else '99:99'")
for t in schedule.sort_by_time():
    slot = t.startTime.strftime("%H:%M") if t.startTime else "99:99"
    print(f"  {slot}  {t.title}")
print()
