from datetime import time

from pawpal_system import Frequency, Owner, Pet, Priority, Task


def main() -> None:
    owner = Owner("Jordan", window_start=time(7, 0), window_end=time(20, 0))

    rex = Pet("Rex", "dog")
    mia = Pet("Mia", "cat")
    owner.add_pet(rex)
    owner.add_pet(mia)

    rex.add_task(Task("Morning walk", time(7, 30), 30, Priority.HIGH, Frequency.DAILY))
    mia.add_task(Task("Breakfast", time(8, 0), 10, Priority.HIGH, Frequency.DAILY))
    rex.add_task(Task("Grooming", time(17, 0), 45, Priority.LOW, Frequency.WEEKLY))
    mia.add_task(Task("Play session", time(12, 30), 20))

    # Placeholder ordering by start time; Scheduler.build_plan() isn't implemented yet.
    print(f"Today's Schedule for {owner.name} "
          f"({owner.window_start:%H:%M}-{owner.window_end:%H:%M})")
    row = "{:<11} | {:<8} | {:<14} | {:<8} | {}"
    print(row.format("Time", "Pet Name", "Activity", "Priority", "Frequency"))
    print("-" * 60)
    for pet, task in sorted(owner.get_all_tasks(), key=lambda pt: pt[1].start_time):
        print(row.format(
            f"{task.start_time:%H:%M}-{task.end_time():%H:%M}",
            pet.name,
            task.name,
            task.priority.name,
            task.frequency.value,
        ))


if __name__ == "__main__":
    main()
