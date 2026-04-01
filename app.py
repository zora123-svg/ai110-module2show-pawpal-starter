import streamlit as st
from pawpal_system import Owner, Pet, Task, DailySchedule, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Session state — initialize each object once; persist across reruns
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner()

if "pet" not in st.session_state:
    st.session_state.pet = Pet(petId=1, ownerId=1, name="", type="")

if "schedule" not in st.session_state:
    st.session_state.schedule = DailySchedule()

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Handy local aliases
owner    = st.session_state.owner
schedule = st.session_state.schedule

# ---------------------------------------------------------------------------
# Section 1 — Owner & Pet setup
# ---------------------------------------------------------------------------
st.subheader("Owner & Pet")

owner_name = st.text_input("Owner name", value=owner.name or "Jordan")
pet_name   = st.text_input("Pet name",   value=st.session_state.pet.name or "Mochi")
species    = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save owner & pet"):
    # Wire owner info → Owner.enterInfo()
    owner.ownerId = 1
    owner.enterInfo(name=owner_name, age=0, dob=None, email="", phone="")

    # Wire pet info → Pet.enterInfo(), then Owner.addPet()
    pet = st.session_state.pet
    pet.enterInfo(name=pet_name, type=species, age=0, breed="")

    if pet not in owner.pets:
        owner.addPet(pet)       # ← Owner.addPet() links pet to owner

    st.success(f"Saved! {owner.displayInfo()}")

# ---------------------------------------------------------------------------
# Section 2 — Add tasks to the pet
# ---------------------------------------------------------------------------
st.markdown("### Tasks")
st.caption("Tasks are added to your Pet, then collected by the scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet  = st.session_state.pet
    task = Task(
        taskId=len(st.session_state.tasks) + 1,
        title=task_title,
        dayOfWeek=__import__("datetime").date.today().strftime("%A"),
        duration=int(duration),
    )
    task.setPriority(Priority[priority_str.upper()])  # ← Task.setPriority()
    pet.addTask(task)                                  # ← Pet.addTask()
    st.session_state.tasks.append({
        "title": task.title,
        "duration (min)": task.duration,
        "priority": task.priority.value,
        "day": task.dayOfWeek,
    })

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")
st.caption("Pulls all tasks from your pets and organises them into today's schedule.")

if st.button("Generate schedule"):
    schedule.scheduleDate = __import__("datetime").date.today()
    schedule.loadFromOwner(owner)           # ← DailySchedule.loadFromOwner()

    if schedule.tasks:
        st.success("Schedule generated!")
        st.text(schedule.displaySchedule()) # ← DailySchedule.displaySchedule()
        used      = schedule.getTotalDuration()
        cap       = DailySchedule.MAX_DAILY_MINUTES
        remaining = cap - used
        st.progress(min(used / cap, 1.0))
        if remaining >= 0:
            st.caption(f"{used} min used · {remaining} min remaining (cap: {cap} min)")
        else:
            st.warning(f"Over cap by {abs(remaining)} min!")
    else:
        st.warning("No tasks found for today. Add tasks above and save your pet first.")
