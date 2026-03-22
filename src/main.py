import asyncio
import json
import os
import subprocess

class WorkflowEngine:
    def __init__(self, workflow_path):
        self.workflow_path = workflow_path
        self.workflow_steps = []

    async def execute_step(self, step):
        step_type = step['type']
        if step_type == 'command':
            command = step['command']
            result = await self.run_command(command)
            return result
        elif step_type == 'function':
            function_name = step['function']
            function = getattr(self, function_name)
            result = await function()
            return result
        else:
            raise ValueError(f'Invalid step type: {step_type}')

    async def run_command(self, command):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
        return stdout.decode().strip()

    async def execute_workflow(self):
        for step in self.workflow_steps:
            result = await self.execute_step(step)
            print(f'Step result: {result}')

    def load_workflow(self):
        with open(self.workflow_path, 'r') as f:
            workflow = json.load(f)
        self.workflow_steps = workflow['steps']

    async def custom_function(self):
        # Add custom functionality here
        return 'Custom function executed successfully'

if __name__ == '__main__':
    workflow_path = os.path.join('workflows', 'example_workflow.json')
    engine = WorkflowEngine(workflow_path)
    engine.load_workflow()
    asyncio.run(engine.execute_workflow())