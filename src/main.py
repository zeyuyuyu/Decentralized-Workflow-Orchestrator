import asyncio
import json
import os
import time

from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.tasks: Dict[str, WorkflowTask] = {}

    def register_workflow(self, workflow: 'Workflow') -> None:
        self.workflows[workflow.name] = workflow

    def register_task(self, task: 'WorkflowTask') -> None:
        self.tasks[task.name] = task

    async def execute_workflow(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        workflow = self.workflows.get(workflow_name)
        if not workflow:
            raise ValueError(f'Workflow "{workflow_name}" not found.')

        workflow_state = WorkflowState(input_data)
        await self._execute_workflow_steps(workflow, workflow_state)
        return workflow_state.output

    async def _execute_workflow_steps(self, workflow: 'Workflow', workflow_state: 'WorkflowState') -> None:
        for step in workflow.steps:
            task = self.tasks.get(step.task_name)
            if not task:
                raise ValueError(f'Task "{step.task_name}" not found.')

            workflow_state.current_step = step
            workflow_state.current_task = task
            await task.execute(workflow_state)

class Workflow:
    def __init__(self, name: str, steps: List['WorkflowStep']):
        self.name = name
        self.steps = steps

class WorkflowStep:
    def __init__(self, task_name: str):
        self.task_name = task_name

class WorkflowTask:
    def __init__(self, name: str, execute: Callable[[WorkflowState], Awaitable[None]]):
        self.name = name
        self.execute = execute

class WorkflowState:
    def __init__(self, input_data: Dict[str, Any]):
        self.input = input_data
        self.output: Dict[str, Any] = {}
        self.current_step: Optional[WorkflowStep] = None
        self.current_task: Optional[WorkflowTask] = None
