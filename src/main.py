import asyncio
import json
import os
import uuid
from typing import Dict, List, Tuple

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, List[Tuple[str, str]]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}

    async def execute_workflow(self, workflow_id: str):
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found.")
        
        for task_id, task_func in self.workflows[workflow_id]:
            self.tasks[task_id] = asyncio.create_task(self._execute_task(task_id, task_func))
        
        await asyncio.gather(*self.tasks.values())

    async def _execute_task(self, task_id: str, task_func: str):
        print(f"Executing task '{task_id}'")
        # Execute the task function here
        await asyncio.sleep(1)
        print(f"Task '{task_id}' completed")

    def register_workflow(self, workflow_id: str, tasks: List[Tuple[str, str]]):
        self.workflows[workflow_id] = tasks

engine = WorkflowEngine()

engine.register_workflow(
    "my_workflow",
    [
        ("task1", "task1_func"),
        ("task2", "task2_func"),
        ("task3", "task3_func"),
    ],
)

async def main():
    await engine.execute_workflow("my_workflow")

asyncio.run(main())