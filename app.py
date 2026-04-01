import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

DATA_FILE = "data.json"
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}

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

st.subheader("Owner Setup")
if "owner" not in st.session_state:
    st.session_state.owner = Owner.load_from_json(DATA_FILE) or Owner(
        name="Jordan",
        daily_available_minutes=90,
    )

owner: Owner = st.session_state.owner
owner_name = st.text_input("Owner name", value=owner.name)
daily_minutes = st.number_input(
    "Daily available minutes",
    min_value=1,
    max_value=480,
    value=int(owner.daily_available_minutes),
)
owner.name = owner_name
owner.update_availability(int(daily_minutes))

if st.button("Save owner profile"):
    owner.save_to_json(DATA_FILE)
    st.success("Owner profile saved.")

st.markdown("### Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=4)

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species, age=int(pet_age)))
    owner.save_to_json(DATA_FILE)
    st.success(f"Added pet {pet_name}.")

if owner.pets:
    st.write("Current pets:")
    st.table(
        [
            {"name": pet.name, "species": pet.species, "age": pet.age, "tasks": len(pet.tasks)}
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Assign tasks to a selected pet.")

if owner.pets:
    selected_pet_name = st.selectbox("Assign task to pet", [pet.name for pet in owner.pets])
else:
    selected_pet_name = None

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0)
with col5:
    due_time = st.text_input("Due time (HH:MM)", value="09:00")

if st.button("Add task"):
    if selected_pet_name is None:
        st.warning("Add a pet before adding tasks.")
    else:
        selected_pet = next((pet for pet in owner.pets if pet.name == selected_pet_name), None)
        if selected_pet is not None:
            try:
                selected_pet.add_task(
                    Task(
                        description=task_title,
                        duration_minutes=int(duration),
                        frequency=frequency,
                        priority=priority,
                        due_time=due_time,
                    )
                )
                owner.save_to_json(DATA_FILE)
                st.success(f"Added task to {selected_pet.name}.")
            except ValueError as exc:
                st.warning(f"Could not add task: {exc}")
        else:
            st.warning("Could not find the selected pet.")

scheduler_mode = st.selectbox(
    "Scheduling strategy",
    ["priority_first", "weighted_priority", "shortest_first"],
    index=0,
)
scheduler = Scheduler(strategy=scheduler_mode)
all_tasks = scheduler.retrieve_tasks(owner, include_completed=True)

st.markdown("### Task Filters")
filter_col1, filter_col2 = st.columns(2)
with filter_col1:
    pet_filter_options = ["All pets"] + [pet.name for pet in owner.pets]
    selected_filter_pet = st.selectbox("Filter by pet", pet_filter_options)
with filter_col2:
    status_filter = st.selectbox("Filter by status", ["all", "completed", "incomplete"], index=0)

filtered_tasks = all_tasks
if selected_filter_pet != "All pets":
    filtered_tasks = scheduler.filter_tasks(filtered_tasks, pet_name=selected_filter_pet)
if status_filter == "completed":
    filtered_tasks = scheduler.filter_tasks(filtered_tasks, completed=True)
elif status_filter == "incomplete":
    filtered_tasks = scheduler.filter_tasks(filtered_tasks, completed=False)

sorted_filtered_tasks = scheduler.sort_by_time(filtered_tasks) if filtered_tasks else []

if sorted_filtered_tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "priority": f"{PRIORITY_EMOJI.get(entry['task'].priority, '⚪')} {entry['task'].priority}",
                "pet": entry["pet"].name,
                "task": entry["task"].description,
                "due_date": entry["task"].due_date.isoformat(),
                "due_time": entry["task"].due_time,
                "duration_minutes": entry["task"].duration_minutes,
                "frequency": entry["task"].frequency,
                "urgency_score": round(entry["task"].calculate_weighted_urgency_score(), 2),
                "completed": "✅" if entry["task"].completed else "⭕",
            }
            for entry in sorted_filtered_tasks
        ]
    )
else:
    st.info("No tasks match your current filters.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a schedule using your Scheduler class.")

if st.button("Generate schedule"):
    plan = scheduler.generate_daily_plan(owner)
    if plan:
        st.success("Schedule generated.")
        st.table(
            [
                {
                    "priority": f"{PRIORITY_EMOJI.get(str(item['priority']), '⚪')} {item['priority']}",
                    "pet": item["pet_name"],
                    "task": item["task_description"],
                    "due": f"{item['due_date']} {item['due_time']}",
                    "duration_minutes": item["duration_minutes"],
                    "window": item["window"],
                }
                for item in plan
            ]
        )

        next_slot = scheduler.find_next_available_slot(
            scheduler.retrieve_tasks(owner, include_completed=False),
            duration_minutes=15,
        )
        if next_slot:
            st.info(f"Next available 15-minute slot: {next_slot}")

        if scheduler.conflict_warnings:
            for warning in scheduler.conflict_warnings:
                st.warning(
                    f"Scheduling conflict detected: {warning}. Consider adjusting one task time."
                )
        else:
            st.success("No scheduling conflicts detected.")
        st.write("Why this plan:")
        for explanation in scheduler.explanation_log:
            st.write(f"- {explanation}")
    else:
        st.warning("No incomplete tasks available to schedule.")
