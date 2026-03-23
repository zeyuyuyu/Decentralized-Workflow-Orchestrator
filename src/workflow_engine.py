import asyncio
from typing import List, Dict, Any, Callable
from dataclasses import dataclass

@dataclass
class Task:
    name: str
    func: Callable
    dependencies: List[str] = None
    timeout: int = 300  # 5 min default timeout

class WorkflowEngine:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.results: Dict[str, Any] = {}

    def register_task(self, name: str, func: Callable, dependencies: List[str] = None, timeout: int = 300):
        """Register a task with the workflow engine"""
        self.tasks[name] = Task(name=name, func=func, dependencies=dependencies or [], timeout=timeout)

    async def execute_task(self, task: Task) -> Any:
        """Execute a single task with timeout"""
        try:
            if asyncio.iscoroutinefunction(task.func):
                result = await asyncio.wait_for(task.func(), timeout=task.timeout)
            else:
                result = await asyncio.wait_for(asyncio.to_thread(task.func), timeout=task.timeout)
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(f"Task {task.name} timed out after {task.timeout} seconds")

    async def execute_workflow(self) -> Dict[str, Any]:
        """Execute the entire workflow with parallel execution where possible"""
        while self.tasks:
            # Find all tasks whose dependencies are satisfied
            ready_tasks = [
                task for task in self.tasks.values()
                if all(dep in self.results for dep in task.dependencies)
            ]

            if not ready_tasks:
                if self.tasks:
                    raise ValueError("Circular dependency detected in workflow")
                break

            # Execute ready tasks in parallel
            tasks_to_await = [
                self.execute_task(task) for task in ready_tasks
            ]
            completed_results = await asyncio.gather(*tasks_to_await, return_exceptions=True)

            # Store results and remove completed tasks
            for task, result in zip(ready_tasks, completed_results):
                if isinstance(result, Exception):
                    raise result
                self.results[task.name] = result
                del self.tasks[task.name]

        return self.results

    def run(self) -> Dict[str, Any]:
        """Synchronous entry point to execute the workflow"""
        return asyncio.run(self.execute_workflow())
