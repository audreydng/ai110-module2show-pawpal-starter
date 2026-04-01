# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- Multi-pet ownership model with per-pet task management.
- Time-aware task sorting using `HH:MM` due times.
- Task filtering by pet and completion status.
- Priority-aware daily schedule generation.
- Weighted priority scheduling that blends urgency and priority.
- Recurring task rollover for daily and weekly tasks.
- Lightweight conflict warnings for exact same-time collisions.
- Next-available-slot suggestion for quick schedule planning.
- JSON persistence (`data.json`) so pets/tasks survive app restarts.
- Streamlit UI integration for adding pets/tasks and generating schedules.

## Agent Mode Usage

Agent Mode was used to plan and implement the advanced logic layer in focused iterations:

- Planned `Owner.save_to_json` and `Owner.load_from_json` with custom dictionary serialization.
- Applied a weighted-priority ranking algorithm (`weighted_priority` strategy) for smarter task ordering.
- Integrated persistence into Streamlit session startup and save points after add-pet/add-task actions.
- Improved UI readability with priority emoji indicators and urgency scores.

## 📸 Demo

<a href="/course_images/ai110/pawpal_app_demo.png" target="_blank"><img src='/course_images/ai110/pawpal_app_demo.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The current PawPal+ logic includes lightweight scheduling algorithms to make planning more useful:

- Sorting tasks by due time (`HH:MM`) before planning.
- Filtering tasks by pet name and completion status.
- Auto-generating next occurrences for recurring daily/weekly tasks when completed.
- Detecting same-time conflicts and returning warnings instead of crashing.
- Weighted priority scoring for urgency-aware ranking.
- Finding the next available free slot for quick rescheduling.

## Testing PawPal+

Run the automated tests with:

```bash
python -m pytest
```

The test suite covers:

- Task completion and task addition behavior.
- Time-based sorting correctness.
- Recurring daily task rollover after completion.
- Lightweight conflict detection for duplicate times.
- Edge case handling for pets with no tasks.

Confidence Level: 4/5 stars based on passing automated tests for core scheduling flows and key edge cases.
