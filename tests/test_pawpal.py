from datetime import date, timedelta
from pathlib import Path

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_updates_status() -> None:
    task = Task(description="Walk", duration_minutes=20, frequency="daily", priority="high")

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    initial_count = len(pet.tasks)

    pet.add_task(Task(description="Feed", duration_minutes=10, frequency="daily", priority="high"))

    assert len(pet.tasks) == initial_count + 1


def test_sorting_tasks_by_time_is_chronological() -> None:
    owner = Owner(name="Jordan", daily_available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Evening walk", duration_minutes=25, due_time="18:00"))
    pet.add_task(Task(description="Morning feed", duration_minutes=10, due_time="07:30"))
    pet.add_task(Task(description="Lunch meds", duration_minutes=5, due_time="12:15"))
    owner.add_pet(pet)

    scheduler = Scheduler()
    sorted_entries = scheduler.sort_by_time(scheduler.retrieve_tasks(owner))

    sorted_times = [entry["task"].due_time for entry in sorted_entries]
    assert sorted_times == ["07:30", "12:15", "18:00"]


def test_marking_daily_task_complete_creates_next_day_task() -> None:
    owner = Owner(name="Jordan", daily_available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=4)
    today = date.today()
    pet.add_task(
        Task(
            description="Morning walk",
            duration_minutes=20,
            frequency="daily",
            due_time="08:00",
            due_date=today,
        )
    )
    owner.add_pet(pet)

    scheduler = Scheduler()
    completed = scheduler.complete_task(owner, pet_name="Mochi", task_description="Morning walk")

    assert completed is True
    assert len(pet.tasks) == 2

    completed_task = pet.tasks[0]
    next_task = pet.tasks[1]
    assert completed_task.completed is True
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.description == "Morning walk"


def test_detect_conflicts_flags_duplicate_times() -> None:
    owner = Owner(name="Jordan", daily_available_minutes=120)
    dog = Pet(name="Mochi", species="dog", age=4)
    cat = Pet(name="Luna", species="cat", age=8)

    dog.add_task(Task(description="Walk", duration_minutes=20, due_time="09:00"))
    cat.add_task(Task(description="Feed", duration_minutes=10, due_time="09:00"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler()
    warnings = scheduler.detect_conflicts(scheduler.retrieve_tasks(owner))

    assert len(warnings) == 1
    assert "Conflict at" in warnings[0]
    assert "Mochi: Walk" in warnings[0]
    assert "Luna: Feed" in warnings[0]


def test_pet_with_no_tasks_returns_empty_schedule() -> None:
    owner = Owner(name="Jordan", daily_available_minutes=60)
    owner.add_pet(Pet(name="Mochi", species="dog", age=4))

    scheduler = Scheduler()
    plan = scheduler.generate_daily_plan(owner)

    assert plan == []


def test_owner_persistence_roundtrip(tmp_path: Path) -> None:
    data_path = tmp_path / "data.json"
    owner = Owner(name="Jordan", daily_available_minutes=90)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Morning walk", duration_minutes=25, due_time="08:30"))
    owner.add_pet(pet)

    owner.save_to_json(str(data_path))
    loaded_owner = Owner.load_from_json(str(data_path))

    assert loaded_owner is not None
    assert loaded_owner.name == "Jordan"
    assert len(loaded_owner.pets) == 1
    assert loaded_owner.pets[0].tasks[0].description == "Morning walk"


def test_priority_first_sorts_by_priority_then_time() -> None:
    owner = Owner(name="Jordan", daily_available_minutes=120)
    pet = Pet(name="Mochi", species="dog", age=4)
    pet.add_task(Task(description="Medium early", duration_minutes=20, priority="medium", due_time="07:00"))
    pet.add_task(Task(description="High later", duration_minutes=20, priority="high", due_time="09:00"))
    pet.add_task(Task(description="High earlier", duration_minutes=20, priority="high", due_time="08:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(strategy="priority_first")
    ranked = scheduler.rank_tasks(scheduler.retrieve_tasks(owner, include_completed=True))

    assert [entry["task"].description for entry in ranked] == [
        "High earlier",
        "High later",
        "Medium early",
    ]
