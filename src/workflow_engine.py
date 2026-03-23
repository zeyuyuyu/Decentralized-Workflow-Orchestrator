import asyncio
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

@dataclass
class Task:
    id: str
    dependencies: Set[str]
    action: callable
    status: TaskStatus = TaskStatus.PENDING

class WorkflowEngine:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, any] = {}

    def add_task(self, task_id: str, action: callable, dependencies: Set[str] = None):
        """Register a new task with optional dependencies"""
        self.tasks[task_id] = Task(
            id=task_id,
            action=action,
            dependencies=dependencies or set()
        )

    async def execute_task(self, task: Task):
        """Execute a single task and store its result"""
        try:
            task.status = TaskStatus.RUNNING
            if asyncio.iscoroutinefunction(task.action):
                result = await task.action()
            else:
                result = await asyncio.get_event_loop().run_in_executor(None, task.action)
            task.status = TaskStatus.COMPLETED
            self.results[task.id] = result
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            raise e

    def get_ready_tasks(self) -> List[Task]:
        """Return list of tasks whose dependencies are satisfied"""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                if all(self.tasks[dep].status == TaskStatus.COMPLETED 
                       for dep in task.dependencies):
                    ready_tasks.append(task)
        return ready_tasks

    async def execute_workflow(self, max_parallel: int = 5):
        """Execute workflow with parallel task processing"""
        while True:
            ready_tasks = self.get_ready_tasks()
            if not ready_tasks:
                if all(task.status == TaskStatus.COMPLETED for task in self.tasks.values()):
                    break
                elif any(task.status == TaskStatus.FAILED for task in self.tasks.values()):
                    raise Exception('Workflow failed due to task failure')
                await asyncio.sleep(0.1)
                continue

            # Execute ready tasks in parallel up to max_parallel
            tasks = [self.execute_task(task) for task in ready_tasks[:max_parallel]]
            await asyncio.gather(*tasks)

        return self.results

    def reset(self):
        """Reset workflow state"""
        for task in self.tasks.values():
            task.status = TaskStatus.PENDING
        self.results.clear()
