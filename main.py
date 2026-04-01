import importlib

from pawpal_system import Owner, Pet, Scheduler, Task

tabulate_module = importlib.import_module("tabulate") if importlib.util.find_spec("tabulate") else None
tabulate = getattr(tabulate_module, "tabulate", None) if tabulate_module else None


PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def print_schedule(plan: list[dict[str, object]]) -> None:
    print("Today's Schedule")
    print("=" * 40)
    if not plan:
        print("No tasks scheduled.")
        return

    rows = []
    for idx, item in enumerate(plan, start=1):
        rows.append(
            [
                idx,
                item["pet_name"],
                item["task_description"],
                f"{PRIORITY_EMOJI.get(str(item['priority']), '⚪')} {item['priority']}",
                f"{item['due_date']} {item['due_time']}",
                item["duration_minutes"],
                f"{item['start_minute']}-{item['end_minute']}",
            ]
        )

    headers = ["#", "Pet", "Task", "Priority", "Due", "Minutes", "Slot"]
    if tabulate:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        print(headers)
        for row in rows:
            print(row)


def print_task_entries(title: str, entries: list[dict[str, object]]) -> None:
    print(title)
    print("-" * 40)
    rows = []
    for entry in entries:
        pet = entry["pet"]
        task = entry["task"]
        rows.append(
            [
                pet.name,
                task.description,
                f"{PRIORITY_EMOJI.get(task.priority, '⚪')} {task.priority}",
                f"{task.due_date.isoformat()} {task.due_time}",
                "✅" if task.completed else "⭕",
            ]
        )

    headers = ["Pet", "Task", "Priority", "Due", "Status"]
    if rows:
        if tabulate:
            print(tabulate(rows, headers=headers, tablefmt="github"))
        else:
            print(headers)
            for row in rows:
                print(row)
    if not entries:
        print("No matching tasks.")
    print()


def main() -> None:
    owner = Owner(
        name="Jordan",
        daily_available_minutes=90,
        preferred_time_windows=["morning", "evening"],
    )

    dog = Pet(name="Mochi", species="dog", age=4, energy_level="high")
    cat = Pet(name="Luna", species="cat", age=9, energy_level="medium")

    # Add tasks intentionally out of order to test sort_by_time.
    dog.add_task(
        Task(
            description="Play session",
            duration_minutes=20,
            frequency="daily",
            priority="medium",
            due_time="13:30",
        )
    )
    dog.add_task(
        Task(
            description="Morning walk",
            duration_minutes=30,
            frequency="daily",
            priority="high",
            due_time="08:00",
        )
    )
    cat.add_task(
        Task(
            description="Feed dinner",
            duration_minutes=10,
            frequency="daily",
            priority="high",
            due_time="08:00",
        )
    )
    cat.add_task(
        Task(
            description="Brush coat",
            duration_minutes=15,
            frequency="weekly",
            priority="low",
            due_time="18:45",
        )
    )

    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(strategy="weighted_priority")

    all_entries = scheduler.retrieve_tasks(owner, include_completed=True)
    sorted_entries = scheduler.sort_by_time(all_entries)
    print_task_entries("All Tasks (sorted by time)", sorted_entries)

    initial_conflicts = scheduler.detect_conflicts(sorted_entries)
    if initial_conflicts:
        print("Conflict Warnings (before completion)")
        print("=" * 40)
        for warning in initial_conflicts:
            print(f"- {warning}")
        print()

    luna_entries = scheduler.filter_tasks(all_entries, pet_name="Luna")
    print_task_entries("Filtered Tasks (pet=Luna)", luna_entries)

    scheduler.complete_task(owner, pet_name="Mochi", task_description="Morning walk")
    incomplete_entries = scheduler.filter_tasks(
        scheduler.retrieve_tasks(owner, include_completed=True), completed=False
    )
    print_task_entries("Incomplete Tasks After Completing 'Morning walk'", incomplete_entries)

    plan = scheduler.generate_daily_plan(owner)
    print_schedule(plan)

    if scheduler.conflict_warnings:
        print("\nConflict Warnings")
        print("=" * 40)
        for warning in scheduler.conflict_warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
