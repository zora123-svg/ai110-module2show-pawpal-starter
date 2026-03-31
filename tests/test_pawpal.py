from pawpal_system import Task, Pet, Priority


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
