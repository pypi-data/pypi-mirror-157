import time
from typing import List

TEMPLATE = """
-----------------------------------------
ms     %     Task name
-----------------------------------------
{}
-----------------------------------------
{}
"""
LINE = "{:<13}{}"


class StopWatch:
    """timing of a number of tasks"""

    def __init__(self, name="") -> None:
        self.id: str = name
        self.task_list: List["TaskInfo"] = []
        self.running: bool = False
        self.start_millis: int = int(time.time() * 1000)
        self.current_task_start_time_millis: int = 0
        self.current_task_name: str = ""
        self.total_time_millis = 0

    def start(self, name):
        if self.running:
            raise Exception("Can't start StopWatch: it's already running")

        self.running = True
        self.current_task_start_time_millis = time.time()
        self.current_task_name = name

    def stop(self):
        if not self.running:
            raise Exception("Can't stop StopWatch: it's not running")

        last_time = int((time.time() - self.current_task_start_time_millis) * 1000)
        task_info = TaskInfo(self.current_task_name, last_time)
        self.task_list.append(task_info)
        self.running = False
        self.total_time_millis = int(time.time() * 1000) - self.start_millis

    def pretty_print(self):
        body = "\n".join(
            LINE.format(task_info.time_millis, task_info.task_name)
            for task_info in self.task_list
        )
        total = LINE.format(self.total_time_millis, "total")
        return TEMPLATE.format(body, total)


class TaskInfo:
    def __init__(self, task_name: str, time_millis: int) -> None:
        self.task_name = task_name
        self.time_millis = time_millis

    def __str__(self) -> str:
        return f"{self.task_name} "
