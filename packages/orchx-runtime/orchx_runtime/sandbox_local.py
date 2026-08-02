import asyncio
import os
import time
from typing import Dict

from orchx_core.interfaces.sandbox import Sandbox, ExecutionContext, SandboxResult


class LocalProcessSandbox(Sandbox):
    """
    Spawns task shell commands in a local host subprocess.
    """

    async def execute(self, context: ExecutionContext) -> SandboxResult:
        start_time = time.time()
        
        # Resolve executing command from metadata
        command = context.task.metadata.get("command", "echo 'Executing OrchX Sandbox command'")
        
        # Prepare environment variables
        env = os.environ.copy()
        if context.env_vars:
            env.update(context.env_vars)

        # Confirm working directory exists
        cwd = context.working_directory
        if not os.path.exists(cwd):
            try:
                os.makedirs(cwd, exist_ok=True)
            except Exception:
                cwd = None  # Fallback to current directory

        stdout_data, stderr_data = b"", b""
        exit_code = -1

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd
            )
            
            # Read streams asynchronously
            stdout_bytes, stderr_bytes = await process.communicate()
            stdout_data = stdout_bytes
            stderr_data = stderr_bytes
            exit_code = process.returncode
        except Exception as e:
            stderr_data = f"Failed to spawn local sandbox process: {e}".encode("utf-8")
            exit_code = 127

        duration = time.time() - start_time
        
        # Populate result fields
        return SandboxResult(
            execution_id=context.execution_id,
            exit_code=exit_code,
            stdout=stdout_data.decode("utf-8", errors="replace"),
            stderr=stderr_data.decode("utf-8", errors="replace"),
            execution_duration=duration,
            cpu_time=duration * 0.1,  # Mock CPU usage details
            memory_usage=1024 * 1024 * 5,  # Mock RAM usage
            produced_artifacts=[
                f"art-{context.execution_id}-{out_port}" for out_port in context.task.outputs
            ],
            emitted_events=[]
        )
