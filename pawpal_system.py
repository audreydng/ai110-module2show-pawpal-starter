from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional


PRIORITY_SCORES = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


@dataclass
class Task:
    description: str
    duration_minutes: int
    frequency: str = "daily"
    priority: str = "medium"
    completed: bool = False
    due_time: str = "09:00"
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Validate task fields after initialization."""
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.priority not in PRIORITY_SCORES:
            raise ValueError("priority must be one of: low, medium, high")
        datetime.strptime(self.due_time, "%H:%M")

    def get_priority_score(self) -> int:
        """Return the numeric score for this task's priority."""
        return PRIORITY_SCORES[self.priority]

    def is_mandatory(self) -> bool:
        """Return True when this task should be treated as mandatory."""
        return self.priority == "high"

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_complete(self) -> None:
        """Alias for mark_completed used by simple tests."""
        self.mark_completed()

    def mark_incomplete(self) -> None:
        """Reset the task to an incomplete state."""
        self.completed = False

    def next_occurrence(self) -> Optional["Task"]:
        """Return the next recurring task instance for daily or weekly tasks."""
        frequency_key = self.frequency.lower()
        if frequency_key == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif frequency_key == "weekly":
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            description=self.description,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            completed=False,
            due_time=self.due_time,
            due_date=next_date,
        )

    def calculate_weighted_urgency_score(
        self,
        weight_priority: float = 0.6,
        weight_urgency: float = 0.4,
    ) -> float:
        """Blend priority score and due-time urgency into a single weighted score."""
        now = datetime.now()
        hour, minute = map(int, self.due_time.split(":"))
        due_dt = datetime.combine(self.due_date, datetime.min.time()).replace(
            hour=hour,
            minute=minute,
        )
        hours_until_due = max(0.0, (due_dt - now).total_seconds() / 3600)

        priority_component = self.get_priority_score() / 3.0
        urgency_component = max(0.0, min(1.0, 1.0 - (hours_until_due / 24.0)))
        return (priority_component * weight_priority + urgency_component * weight_urgency) * 10.0

    def to_dict(self) -> dict[str, object]:
        """Serialize task data into a JSON-safe dictionary."""
        return {
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "frequency": self.frequency,
            "priority": self.priority,
            "completed": self.completed,
            "due_time": self.due_time,
            "due_date": self.due_date.isoformat(),
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> "Task":
        """Create a Task instance from a dictionary payload."""
        return Task(
            description=str(data.get("description", "")),
            duration_minutes=int(data.get("duration_minutes", 1)),
            frequency=str(data.get("frequency", "daily")),
            priority=str(data.get("priority", "medium")),
            completed=bool(data.get("completed", False)),
            due_time=str(data.get("due_time", "09:00")),
            due_date=date.fromisoformat(str(data.get("due_date", date.today().isoformat()))),
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    medical_conditions: list[str] = field(default_factory=list)
    energy_level: str = "medium"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a new task to this pet."""
        self.tasks.append(task)

    def get_tasks(self, include_completed: bool = False) -> list[Task]:
        """Return tasks, optionally including completed tasks."""
        if include_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.completed]

    def get_required_categories(self) -> list[str]:
        """Return required care categories inferred from medical conditions."""
        if "diabetes" in [condition.lower() for condition in self.medical_conditions]:
            return ["medication", "feeding"]
        return []

    def is_task_appropriate(self, task: Task) -> bool:
        """Check whether a task duration is suitable for this pet profile."""
        # Older pets should avoid very long sessions.
        if self.age >= 10 and task.duration_minutes > 60:
            return False
        return True

    def to_dict(self) -> dict[str, object]:
        """Serialize pet data including tasks into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "medical_conditions": self.medical_conditions,
            "energy_level": self.energy_level,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> "Pet":
        """Create a Pet instance from a dictionary payload."""
        pet = Pet(
            name=str(data.get("name", "Unknown")),
            species=str(data.get("species", "other")),
            age=int(data.get("age", 0)),
            medical_conditions=list(data.get("medical_conditions", [])),
            energy_level=str(data.get("energy_level", "medium")),
        )
        for task_data in list(data.get("tasks", [])):
            pet.add_task(Task.from_dict(task_data))
        return pet


@dataclass
class Owner:
    name: str
    daily_available_minutes: int
    preferred_time_windows: list[str] = field(default_factory=list)
    priority_style: str = "balanced"
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return a pet by name if it exists for this owner."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def update_availability(self, minutes: int) -> None:
        """Update the owner's daily available minutes."""
        if minutes < 0:
            raise ValueError("daily_available_minutes cannot be negative")
        self.daily_available_minutes = minutes

    def get_all_tasks(self, include_completed: bool = False) -> list[dict[str, object]]:
        """Aggregate tasks across all pets as pet-task entries."""
        all_tasks: list[dict[str, object]] = []
        for pet in self.pets:
            for task in pet.get_tasks(include_completed=include_completed):
                all_tasks.append({"pet": pet, "task": task})
        return all_tasks

    def can_accept_task(self, task: Task) -> bool:
        """Return whether the task fits the owner's daily time budget."""
        return task.duration_minutes <= self.daily_available_minutes

    def to_dict(self) -> dict[str, object]:
        """Serialize owner data including pets/tasks into a JSON-safe dictionary."""
        return {
            "name": self.name,
            "daily_available_minutes": self.daily_available_minutes,
            "preferred_time_windows": self.preferred_time_windows,
            "priority_style": self.priority_style,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> "Owner":
        """Create an Owner instance from a dictionary payload."""
        owner = Owner(
            name=str(data.get("name", "Jordan")),
            daily_available_minutes=int(data.get("daily_available_minutes", 90)),
            preferred_time_windows=list(data.get("preferred_time_windows", [])),
            priority_style=str(data.get("priority_style", "balanced")),
        )
        for pet_data in list(data.get("pets", [])):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, file_path: str = "data.json") -> None:
        """Persist owner, pet, and task state to a JSON file."""
        target = Path(file_path)
        target.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @staticmethod
    def load_from_json(file_path: str = "data.json") -> Optional["Owner"]:
        """Load owner state from JSON when the file is present and valid."""
        target = Path(file_path)
        if not target.exists():
            return None
        try:
            payload = json.loads(target.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return Owner.from_dict(payload)


class Scheduler:
    def __init__(self, strategy: str = "priority_first") -> None:
        """Initialize scheduler strategy and run metadata."""
        self.strategy = strategy
        self.generated_at: Optional[datetime] = None
        self.explanation_log: list[str] = []
        self.conflict_warnings: list[str] = []

    def retrieve_tasks(self, owner: Owner, include_completed: bool = False) -> list[dict[str, object]]:
        """Fetch aggregated pet tasks from the owner."""
        return owner.get_all_tasks(include_completed=include_completed)

    def generate_daily_plan(
        self,
        owner: Owner,
        available_minutes: Optional[int] = None,
    ) -> list[dict[str, object]]:
        """Build a scheduled daily plan from an owner's pet tasks."""
        minutes_limit = available_minutes or owner.daily_available_minutes
        task_entries = self.retrieve_tasks(owner)
        task_entries = self.filter_tasks(task_entries, completed=False)
        task_entries = self.sort_by_time(task_entries)
        ranked_entries = self.rank_tasks(task_entries)
        selected_entries = self.select_tasks_within_time_limit(ranked_entries, minutes_limit)
        plan = self.assign_time_slots(selected_entries, owner.preferred_time_windows)
        self.conflict_warnings = self.detect_conflicts(selected_entries)

        self.generated_at = datetime.now()
        self.explanation_log = self.explain_choices(plan)
        return plan

    def sort_by_time(self, task_entries: list[dict[str, object]]) -> list[dict[str, object]]:
        """Sort task entries by due_time in HH:MM format."""
        return sorted(
            task_entries,
            key=lambda entry: datetime.strptime(entry["task"].due_time, "%H:%M"),
        )

    def filter_tasks(
        self,
        task_entries: list[dict[str, object]],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[dict[str, object]]:
        """Filter task entries by pet name and/or completion status."""
        filtered = task_entries
        if pet_name is not None:
            filtered = [entry for entry in filtered if entry["pet"].name == pet_name]
        if completed is not None:
            filtered = [entry for entry in filtered if entry["task"].completed == completed]
        return filtered

    def rank_tasks(
        self,
        task_entries: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        """Sort task entries according to the selected scheduling strategy."""
        if self.strategy == "shortest_first":
            return sorted(
                task_entries,
                key=lambda entry: (
                    int(entry["task"].duration_minutes),
                    -int(entry["task"].get_priority_score()),
                ),
            )

        if self.strategy == "weighted_priority":
            return sorted(
                task_entries,
                key=lambda entry: (
                    -float(entry["task"].calculate_weighted_urgency_score()),
                    datetime.strptime(entry["task"].due_time, "%H:%M"),
                ),
            )

        return sorted(
            task_entries,
            key=lambda entry: (
                -int(entry["task"].get_priority_score()),
                datetime.strptime(entry["task"].due_time, "%H:%M"),
                int(entry["task"].duration_minutes),
            ),
        )

    def select_tasks_within_time_limit(
        self,
        task_entries: list[dict[str, object]],
        minutes: int,
    ) -> list[dict[str, object]]:
        """Choose ranked tasks greedily without exceeding the minute limit."""
        selected: list[dict[str, object]] = []
        used_minutes = 0

        for entry in task_entries:
            task = entry["task"]
            task_minutes = int(task.duration_minutes)
            if used_minutes + task_minutes <= minutes:
                selected.append(entry)
                used_minutes += task_minutes
        return selected

    def assign_time_slots(
        self,
        task_entries: list[dict[str, object]],
        windows: list[str],
    ) -> list[dict[str, object]]:
        """Assign sequential minute ranges and a time window label to tasks."""
        plan: list[dict[str, object]] = []
        window_label = windows[0] if windows else "anytime"

        for entry in task_entries:
            pet = entry["pet"]
            task = entry["task"]
            start_dt = datetime.strptime(task.due_time, "%H:%M")
            start_minute = start_dt.hour * 60 + start_dt.minute
            end_minute = start_minute + int(task.duration_minutes)
            plan.append(
                {
                    "pet_name": pet.name,
                    "task_description": task.description,
                    "frequency": task.frequency,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat(),
                    "due_time": task.due_time,
                    "window": window_label,
                    "start_minute": start_minute,
                    "end_minute": end_minute,
                    "duration_minutes": task.duration_minutes,
                }
            )
        return plan

    def detect_conflicts(self, task_entries: list[dict[str, object]]) -> list[str]:
        """Detect exact same-time conflicts and return warning messages."""
        warnings: list[str] = []
        seen_slots: dict[tuple[str, str], list[dict[str, object]]] = {}

        for entry in task_entries:
            task = entry["task"]
            key = (task.due_date.isoformat(), task.due_time)
            seen_slots.setdefault(key, []).append(entry)

        for (due_date_value, due_time_value), entries in seen_slots.items():
            if len(entries) < 2:
                continue
            labels = [f"{entry['pet'].name}: {entry['task'].description}" for entry in entries]
            warnings.append(
                f"Conflict at {due_date_value} {due_time_value} -> " + ", ".join(labels)
            )
        return warnings

    def find_next_available_slot(
        self,
        task_entries: list[dict[str, object]],
        duration_minutes: int,
        day_start: str = "06:00",
        day_end: str = "22:00",
    ) -> Optional[str]:
        """Find the next free HH:MM slot for a given duration within day bounds."""
        start_dt = datetime.strptime(day_start, "%H:%M")
        end_dt = datetime.strptime(day_end, "%H:%M")

        occupied: list[tuple[datetime, datetime]] = []
        for entry in self.sort_by_time(task_entries):
            task = entry["task"]
            task_start = datetime.strptime(task.due_time, "%H:%M")
            task_end = task_start + timedelta(minutes=int(task.duration_minutes))
            occupied.append((task_start, task_end))

        cursor = start_dt
        for occ_start, occ_end in occupied:
            if cursor + timedelta(minutes=duration_minutes) <= occ_start:
                return cursor.strftime("%H:%M")
            if occ_end > cursor:
                cursor = occ_end

        if cursor + timedelta(minutes=duration_minutes) <= end_dt:
            return cursor.strftime("%H:%M")
        return None

    def explain_choices(self, plan: list[dict[str, object]]) -> list[str]:
        """Create plain-language explanations for each scheduled task."""
        explanations: list[str] = []
        for item in plan:
            explanations.append(
                "Selected "
                f"{item['task_description']} for {item['pet_name']} "
                f"because it is {item['priority']} priority and fits in the available schedule."
            )
        return explanations

    def complete_task(self, owner: Owner, pet_name: str, task_description: str) -> bool:
        """Mark a task complete and create next recurring instance when needed."""
        pet = owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description == task_description and not task.completed:
                task.mark_completed()
                next_task = task.next_occurrence()
                if next_task is not None:
                    pet.add_task(next_task)
                return True
        return False
