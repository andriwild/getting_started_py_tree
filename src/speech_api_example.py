from enum import Enum
from dataclasses import dataclass
from datetime import date
from typing import Optional, List

class TaskState(Enum):
    PENDING = 0
    SEARCH = 1
    ENGAGE = 2
    ESCORT_AGREE = 3
    ESCORT_DISAGREE = 4
    HANDOFF = 5
    SUCCESS = 6
    FAIL = 7

@dataclass(frozen=True)
class Task:
    id: int
    person_id: int
    target_room_id: int
    state: TaskState

@dataclass(frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str
    sex: str
    birth_date: date
    assigned_room_id: Optional[int]

@dataclass(frozen=True)
class Room:
    id: int
    name: str

tasks: dict[int, Task] = {}
persons: dict[int, Person] = {}
room: dict[int, Room] = {}

persons[1] = Person(
    id=1,
    first_name="Max",
    last_name="Mustermann",
    sex="m",
    birth_date=date(1990, 1, 1),
    assigned_room_id=1
)

tasks[1] = Task(
    id=1,
    person_id=1,
    target_room_id=1,
    state=TaskState.PENDING
)

room[1] = Room(
    id=1,
    name="Max Raum"
)

room[2] = Room(
    id=2,
    name="Therapie Raum"
)


def fetch_task_by_state(state: TaskState):
    return [task for task in tasks.values() if task.state == state]
    

def update_current_task(task_id: int, new_state: TaskState):
    if task_id not in tasks:
        raise Exception(status_code=404, detail="Task not found")
    old_task = tasks[task_id]
    updated_task = Task(
        id=old_task.id,
        person_id=old_task.person_id,
        target_room_id=old_task.target_room_id,
        state=new_state
    )
    tasks[task_id] = updated_task


def fetch_person_by_id(person_id: int):
    if person_id not in persons:
        raise Exception(status_code=404, detail="Person not found")
    return persons[person_id]


if __name__ == '__main__':
    print(fetch_person_by_id(1))
    print(fetch_task_by_state(TaskState.PENDING))
    update_current_task(1, TaskState.SEARCH)
    print(fetch_task_by_state(TaskState.SEARCH))
