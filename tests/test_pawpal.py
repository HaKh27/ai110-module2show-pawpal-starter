from datetime import date, time, timedelta

from pawpal_system import Frequency, Outcome, Owner, Pet, Priority, Scheduler, Task


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", time(7, 30), 30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Rex", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", time(7, 30), 30))

    assert len(pet.tasks) == 1


def _scheduler_with(task):
    owner = Owner("Jordan", time(7, 0), time(20, 0))
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(task)
    return Scheduler(owner), pet


def test_completing_daily_task_creates_next_day_copy():
    task = Task("Walk", time(7, 30), 30, frequency=Frequency.DAILY)
    scheduler, pet = _scheduler_with(task)

    next_task = scheduler.complete_task(pet, task)

    assert task.completed is True
    assert len(pet.tasks) == 2
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.id != task.id


def test_completing_weekly_task_creates_copy_a_week_later():
    task = Task("Grooming", time(17, 0), 45, frequency=Frequency.WEEKLY)
    scheduler, pet = _scheduler_with(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task.due_date == date.today() + timedelta(days=7)


def test_completing_one_time_task_creates_nothing():
    task = Task("Vet visit", time(10, 0), 60)
    scheduler, pet = _scheduler_with(task)

    assert scheduler.complete_task(pet, task) is None
    assert len(pet.tasks) == 1


def test_completing_a_task_twice_does_not_duplicate_it():
    task = Task("Walk", time(7, 30), 30, frequency=Frequency.DAILY)
    scheduler, pet = _scheduler_with(task)

    scheduler.complete_task(pet, task)
    scheduler.complete_task(pet, task)

    assert len(pet.tasks) == 2


def test_next_due_date_is_based_on_today_even_if_completed_late():
    task = Task("Walk", time(7, 30), 30, frequency=Frequency.DAILY,
                due_date=date.today() - timedelta(days=5))
    scheduler, pet = _scheduler_with(task)

    next_task = scheduler.complete_task(pet, task)

    assert next_task.due_date == date.today() + timedelta(days=1)


def _two_pet_scheduler(task_a, task_b, same_pet=False):
    owner = Owner("Jordan", time(7, 0), time(20, 0))
    rex, mia = Pet("Rex", "dog"), Pet("Mia", "cat")
    owner.add_pet(rex)
    owner.add_pet(mia)
    rex.add_task(task_a)
    (rex if same_pet else mia).add_task(task_b)
    return Scheduler(owner)


def test_find_conflicts_warns_for_same_time_on_different_pets():
    scheduler = _two_pet_scheduler(Task("Walk", time(8, 0), 30), Task("Feed", time(8, 0), 10))

    warnings = scheduler.find_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feed" in warnings[0] and "Rex and Mia" in warnings[0]


def test_find_conflicts_warns_for_overlap_on_same_pet():
    scheduler = _two_pet_scheduler(
        Task("Walk", time(8, 0), 30), Task("Groom", time(8, 15), 30), same_pet=True)

    warnings = scheduler.find_conflicts()

    assert len(warnings) == 1 and "for Rex" in warnings[0]


def test_find_conflicts_ignores_back_to_back_and_completed_tasks():
    back_to_back = _two_pet_scheduler(Task("Walk", time(8, 0), 30), Task("Feed", time(8, 30), 10))
    assert back_to_back.find_conflicts() == []

    done = Task("Walk", time(8, 0), 30)
    done.mark_complete()
    completed = _two_pet_scheduler(done, Task("Feed", time(8, 0), 10))
    assert completed.find_conflicts() == []


def _plan(*tasks, window=(time(7, 0), time(20, 0))):
    """Put the tasks on one pet and return the scheduler after build_plan()."""
    owner = Owner("Jordan", *window)
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    for task in tasks:
        pet.add_task(task)
    scheduler = Scheduler(owner)
    scheduler.build_plan()
    return scheduler


def _entry(scheduler, name):
    return next(e for e in scheduler.scheduled + scheduler.dropped if e.task.name == name)


def test_plan_keeps_non_overlapping_tasks_at_requested_times():
    s = _plan(Task("Walk", time(8, 0), 30), Task("Feed", time(9, 0), 10))

    assert [e.outcome for e in s.scheduled] == [Outcome.KEPT, Outcome.KEPT]
    assert [e.final_start for e in s.scheduled] == [time(8, 0), time(9, 0)]
    assert s.dropped == []


def test_higher_priority_task_keeps_slot_and_lower_is_moved_later():
    s = _plan(Task("Low", time(8, 0), 30, Priority.LOW), Task("High", time(8, 0), 30, Priority.HIGH))

    assert _entry(s, "High").outcome == Outcome.KEPT
    low = _entry(s, "Low")
    assert low.outcome == Outcome.MOVED and low.final_start == time(8, 30)
    assert "High" in low.reason


def test_equal_priority_overlap_goes_to_earlier_time_then_first_created():
    earlier = _plan(Task("B", time(8, 15), 30), Task("A", time(8, 0), 30))
    assert _entry(earlier, "A").outcome == Outcome.KEPT
    assert _entry(earlier, "B").final_start == time(8, 30)

    first, second = Task("First", time(8, 0), 30), Task("Second", time(8, 0), 30)
    same_time = _plan(second, first)  # added in the opposite order
    assert _entry(same_time, "First").outcome == Outcome.KEPT
    assert _entry(same_time, "Second").outcome == Outcome.MOVED


def test_task_moves_past_a_chain_of_blocking_tasks():
    s = _plan(
        Task("A", time(8, 0), 30, Priority.HIGH),
        Task("B", time(8, 30), 30, Priority.HIGH),
        Task("C", time(8, 0), 30, Priority.LOW),
    )

    assert _entry(s, "C").final_start == time(9, 0)


def test_task_is_dropped_when_no_free_slot_before_window_closes():
    s = _plan(
        Task("Big", time(8, 0), 60, Priority.HIGH),
        Task("Small", time(8, 30), 30, Priority.LOW),
        window=(time(7, 0), time(9, 0)),
    )

    small = _entry(s, "Small")
    assert small.outcome == Outcome.DROPPED and small.final_start is None
    assert "no free slot" in small.reason
    assert [e.task.name for e in s.dropped] == ["Small"]


def test_task_outside_the_window_is_dropped():
    s = _plan(Task("Early", time(6, 0), 10), Task("Late", time(19, 50), 30))

    assert {e.task.name for e in s.dropped} == {"Early", "Late"}
    assert all("outside available window" in e.reason for e in s.dropped)
    assert s.scheduled == []


def test_completed_and_other_day_tasks_are_left_out_of_the_plan():
    done = Task("Done", time(8, 0), 30)
    done.mark_complete()
    tomorrow = Task("Tomorrow", time(9, 0), 30, due_date=date.today() + timedelta(days=1))
    s = _plan(done, tomorrow, Task("Today", time(10, 0), 30))

    assert [e.task.name for e in s.scheduled] == ["Today"]
    assert s.dropped == []


def test_every_plan_entry_has_a_reason_and_scheduled_is_sorted_by_time():
    s = _plan(
        Task("C", time(12, 0), 30), Task("A", time(8, 0), 30),
        Task("B", time(8, 0), 30, Priority.LOW), Task("Early", time(5, 0), 10),
    )

    entries = s.scheduled + s.dropped
    assert entries and all(e.reason for e in entries)
    starts = [e.final_start for e in s.scheduled]
    assert starts == sorted(starts)


def test_build_plan_twice_does_not_duplicate_entries_and_plans_across_pets():
    owner = Owner("Jordan", time(7, 0), time(20, 0))
    rex, mia = Pet("Rex", "dog"), Pet("Mia", "cat")
    owner.add_pet(rex)
    owner.add_pet(mia)
    rex.add_task(Task("Walk", time(8, 0), 30))
    mia.add_task(Task("Feed", time(8, 0), 10, Priority.HIGH))
    scheduler = Scheduler(owner)

    scheduler.build_plan()
    scheduler.build_plan()

    assert len(scheduler.scheduled) == 2
    assert {e.pet_name for e in scheduler.scheduled} == {"Rex", "Mia"}
    assert _entry(scheduler, "Walk").final_start == time(8, 10)


import pytest


def test_edit_task_changes_only_the_given_fields():
    pet = Pet("Rex", "dog")
    task = Task("Walk", time(8, 0), 30)
    pet.add_task(task)

    pet.edit_task(task.id, {"duration_minutes": 45, "priority": Priority.HIGH})

    assert (task.duration_minutes, task.priority, task.name) == (45, Priority.HIGH, "Walk")


def test_edit_task_rejects_bad_edits_and_leaves_task_unchanged():
    pet = Pet("Rex", "dog")
    task = Task("Walk", time(8, 0), 30)
    pet.add_task(task)

    with pytest.raises(ValueError):
        pet.edit_task(task.id, {"id": 99})                    # not an editable field
    with pytest.raises(ValueError):
        pet.edit_task(task.id, {"name": "Run", "duration_minutes": 0})  # invalid value
    with pytest.raises(ValueError):
        pet.edit_task(12345, {"name": "Run"})                 # unknown task

    assert (task.name, task.duration_minutes) == ("Walk", 30)


def test_remove_task_removes_it_and_rejects_unknown_ids():
    pet = Pet("Rex", "dog")
    task = Task("Walk", time(8, 0), 30)
    pet.add_task(task)

    pet.remove_task(task.id)
    assert pet.tasks == []
    with pytest.raises(ValueError):
        pet.remove_task(task.id)


def test_edited_and_removed_tasks_change_the_regenerated_plan():
    owner = Owner("Jordan", time(7, 0), time(20, 0))
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    walk, feed = Task("Walk", time(8, 0), 30), Task("Feed", time(8, 0), 10, Priority.HIGH)
    pet.add_task(walk)
    pet.add_task(feed)
    scheduler = Scheduler(owner)

    scheduler.build_plan()
    assert _entry(scheduler, "Walk").outcome == Outcome.MOVED

    pet.edit_task(walk.id, {"start_time": time(10, 0)})
    scheduler.build_plan()
    assert _entry(scheduler, "Walk").outcome == Outcome.KEPT

    pet.remove_task(walk.id)
    scheduler.build_plan()
    assert [e.task.name for e in scheduler.scheduled] == ["Feed"]
