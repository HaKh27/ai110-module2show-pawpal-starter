from datetime import time

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Streamlit reruns this script on every interaction, so keep the Owner in session state.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", time(7, 0), time(20, 0))
owner = st.session_state.owner

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

st.subheader("Owner and Pets")
owner.name = st.text_input("Owner name", value=owner.name)

with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        try:
            owner.add_pet(Pet(pet_name.strip(), species))
        except ValueError as e:
            st.error(str(e))

if owner.pets:
    st.write("Pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    with st.form("add_task_form"):
        # Select by name: Streamlit returns a copy of object options, so look up the real Pet.
        selected_pet = st.selectbox("Pet", [p.name for p in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            start = st.time_input("Start time", value=time(8, 0))
            frequency = st.selectbox(
                "Frequency", list(Frequency), format_func=lambda f: f.value
            )
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox(
                "Priority", list(Priority), index=1, format_func=lambda p: p.name
            )
        if st.form_submit_button("Add task"):
            try:
                pet = next(p for p in owner.pets if p.name == selected_pet)
                pet.add_task(
                    Task(task_title, start, int(duration), priority, frequency)
                )
            except ValueError as e:
                st.error(str(e))
else:
    st.info("Add a pet before adding tasks.")

scheduler = Scheduler(owner)
all_tasks = scheduler.sort_by_time(owner.get_all_tasks())
if all_tasks:
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))
    st.write("Current tasks:")
    st.table(
        [
            {
                "Time": f"{t.start_time:%H:%M}-{t.end_time():%H:%M}",
                "Pet Name": p.name,
                "Activity": t.name,
                "Priority": t.priority.name,
                "Frequency": t.frequency.value,
                "Status": "done" if t.completed else "pending",
            }
            for p, t in all_tasks
        ]
    )

    st.markdown("### Edit or remove a task")
    labels = {
        t.id: f"{p.name}: {t.name} at {t.start_time:%H:%M}" + (" (done)" if t.completed else "")
        for p, t in all_tasks
    }
    task_id = st.selectbox("Task", list(labels), format_func=labels.get)
    pet, task = next((p, t) for p, t in all_tasks if t.id == task_id)
    with st.form("edit_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Task title", value=task.name, key=f"name_{task.id}")
            new_start = st.time_input("Start time", value=task.start_time, key=f"start_{task.id}")
            new_frequency = st.selectbox(
                "Frequency", list(Frequency), index=list(Frequency).index(task.frequency),
                format_func=lambda f: f.value, key=f"freq_{task.id}",
            )
        with col2:
            new_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240,
                value=task.duration_minutes, key=f"dur_{task.id}",
            )
            new_priority = st.selectbox(
                "Priority", list(Priority), index=list(Priority).index(task.priority),
                format_func=lambda p: p.name, key=f"prio_{task.id}",
            )
        save = st.form_submit_button("Save changes")
        complete = st.form_submit_button("Mark complete")
        remove = st.form_submit_button("Remove task")
        if save or complete or remove:
            try:
                if complete:
                    if task.completed:
                        raise ValueError(f"'{task.name}' is already complete")
                    next_task = scheduler.complete_task(pet, task)
                    st.session_state["flash"] = (
                        f"Completed '{task.name}'. Next {task.frequency.value} occurrence "
                        f"added, due {next_task.due_date}."
                        if next_task else f"Completed '{task.name}'."
                    )
                elif save:
                    pet.edit_task(task.id, {
                        "name": new_name, "start_time": new_start,
                        "duration_minutes": int(new_duration),
                        "priority": new_priority, "frequency": new_frequency,
                    })
                else:
                    pet.remove_task(task.id)
                st.rerun()  # redraw the task table with the change
            except ValueError as e:
                st.error(str(e))
elif owner.pets:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Places tasks by priority, moves or drops conflicts, and explains every decision.")

if st.button("Generate schedule"):
    scheduler.build_plan()
    conflicts = scheduler.find_conflicts()
    if conflicts:
        st.warning("Some tasks overlap (the plan below resolves them):\n\n" + "\n\n".join(conflicts))
    if scheduler.scheduled:
        st.success(f"Today's plan for {owner.name}")
        st.table(
            [
                {
                    "Time": e.time_range(),
                    "Pet Name": e.pet_name,
                    "Activity": e.task.name,
                    "Priority": e.task.priority.name,
                    "Outcome": e.outcome.value,
                    "Reason": e.reason,
                }
                for e in scheduler.scheduled
            ]
        )
    else:
        st.info("Nothing to schedule today. Add some tasks above.")
    if scheduler.dropped:
        st.write("Dropped tasks:")
        st.table(
            [
                {
                    "Requested time": e.task.start_time.strftime("%H:%M"),
                    "Pet Name": e.pet_name,
                    "Activity": e.task.name,
                    "Reason": e.reason,
                }
                for e in scheduler.dropped
            ]
        )
